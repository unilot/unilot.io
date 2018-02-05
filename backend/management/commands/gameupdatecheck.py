from django.core.management.base import BaseCommand, CommandError
from web3.main import Web3

from backend.models import Game
from django.utils import timezone
import logging

from backend.serializers import push
from backend.utils.push import PushHelper
from web3.utils.compat import socket

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Checks game update'

    def handle(self, *args, **options):
        try:
            games = Game.objects.filter(status=Game.STATUS_PUBLISHED,
                                        type__in=(Game.TYPE_1_DAY, Game.TYPE_7_DAYS,),
                                        started_at__lte=timezone.now(),
                                        ending_at__gt=timezone.now()).all()

            for game in games:
                if game.smart_contract_id in (None, '', '0'):
                    continue

                logger.info('Processing game %d' % (game.id))

                keep_trying = True

                stat = {}

                while keep_trying:
                    try:
                        stat = game.get_stat()
                        keep_trying = False
                        logger.info('Game %d: Pulling game stats.' % (game.id))
                        logger.debug('Game %d: Stat: %s' % (game.id, str(stat)))
                    except socket.timeout:
                        logger.error('Game %d: Handled timeout error. Trying again.')
                        keep_trying = True

                stat_num_players = stat.get('numPlayers', 0)

                logger.info('Game %d: Checking num players')
                logger.debug('Game %d: Game num players: %d Stat num players: %d' %
                             (game.id, game.num_players, stat_num_players))

                if game.num_players < stat_num_players:
                    logger.info('Game %d: Updating game' % (game.id))
                    game.num_players = stat_num_players
                    game.prize_amount = Web3.fromWei(stat.get('prizeAmount', 0), 'ether')
                    game.save()

                    logger.info('Game %d: Sending notification to debices' % (game.id))
                    push_message = push.GameUpdatedPushMessage(payload=game)
                    PushHelper.inform_all_devices(push_message)

        except Game.DoesNotExist:
            message = 'No games to proceed'
            logger.error(message)
            print(message)

        try:
            games = Game.objects.filter(status=Game.STATUS_PUBLISHED,
                                        type__in=(Game.TYPE_30_DAYS, Game.TOKEN_GAME,),
                                        started_at__lte=timezone.now(),
                                        ending_at__gt=timezone.now()).all()

            for game in games:
                child_games = Game.objects\
                    .exclude(status__in=(Game.STATUS_CANCELED,), type__in=(Game.TYPE_30_DAYS, Game.TOKEN_GAME,))\
                    .filter(started_at__gte=game.started_at, ending_at__lte=game.ending_at).all()

                game.prize_amount = 0
                game.num_players = 0

                for child_game in child_games:
                    game.prize_amount += child_game.prize_amount
                    game.num_players += child_game.num_players

                game.save()

        except Game.DoesNotExist:
            pass
