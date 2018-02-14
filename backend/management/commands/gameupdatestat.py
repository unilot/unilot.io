from pprint import pprint

from django.core.management.base import BaseCommand
from web3.main import Web3

from backend.models import Game, GamePlayer
import logging

from web3.utils.compat import socket

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Updates stat of finished games or pointed via cmd arg'

    def add_arguments(self, parser):
        parser.add_argument('game_id', type=int, nargs='?', default=0)

    def handle(self, *args, **options):
        game_id = options.get('game_id', 0)

        try:
            if game_id > 0:
                games = Game.objects.filter(id=game_id)
            else:
                games = Game.objects\
                    .exclude(status__in=(Game.STATUS_PUBLISHED, Game.STATUS_FINISHING))\
                    .exclude(player__is_winner=True)\
                    .distinct()

            for game in games:

                if not Web3.isAddress(game.smart_contract_id):
                    logger.info('Game %d does not have valid address' % (game.id))
                    continue

                logger.info('Processing game %d' % (game.id))

                keep_trying = True

                stat = {}
                players = []
                winners = {}

                while keep_trying:
                    try:
                        stat = game.get_stat()
                        players = game.get_players()
                        winners = game.get_winners()

                        keep_trying = False

                        logger.info('Game %d: Pulling game stats.' % (game.id))
                        logger.debug('Game %d: Stat: %s' % (game.id, str(stat)))
                    except socket.timeout:
                        logger.error('Game %d: Handled timeout error. Trying again.')
                        keep_trying = True

                stat_num_players = stat.get('numPlayers', 0)

                GamePlayer.objects.filter(game_id=game.id).delete()

                for player in players:
                    GamePlayer.objects.create(game_id=game.id, wallet=player,
                                              is_winner=(player in winners.keys()),
                                              prize_amount=winners.get(player, 0))

                logger.info('Game %d: Checking num players')
                logger.debug('Game %d: Game num players: %d Stat num players: %d' %
                             (game.id, game.num_players, stat_num_players))

                if game.num_players < stat_num_players:
                    logger.info('Game %d: Updating game' % (game.id))
                    game.num_players = stat_num_players
                    game.prize_amount = Web3.fromWei(stat.get('prizeAmount', 0), 'ether')
                    game.save()

        except Game.DoesNotExist:
            message = 'No games to proceed'
            logger.error(message)
            print(message)
