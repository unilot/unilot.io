from django.core.management.base import BaseCommand, CommandError
from backend.models import Game
from django.utils import timezone
import logging

from backend.serializers import push
from backend.utils.push import PushHelper

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Finishes game'
    CONTRACT_NAME = 'UnilotPrizeCalculator'

    def handle(self, *args, **options):
        try:
            games = Game.objects.filter(status__in=(Game.STATUS_PUBLISHED, Game.STATUS_FINISHING), ending_at__lte=timezone.now()).all()

            for game in games:
                if game.smart_contract_id in (None, '', '0'):
                    continue

                if game.status is Game.STATUS_PUBLISHED:
                    try:
                        tx = game.finish()
                    except Exception as e:
                        message = 'Game %d: %s' % (game.id, e)

                        logger.error(message)
                        print(message)

                        continue

                    logger.info('Finish transaction submitted: %s' % (tx))
                    print('For progress see tx: %s' % (tx))
                elif game.get_state() == Game.STATUS_FINISHED:
                    game.status = Game.STATUS_FINISHED
                    game.save()

                    list_of_winners = game.get_winners().keys()

                    gcm_push_message = push.GameFinishedPushMessage(data={'data': list_of_winners}, is_localized=True)
                    apns_push_message = push.GameFinishedPushMessage(data={'data': list_of_winners}, is_localized=False)

                    PushHelper.inform_all_devices(gcm_push_message, apns_push_message)

        except Game.DoesNotExist:
            print('No games to proceed')
