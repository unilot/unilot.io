from django.core.management.base import BaseCommand, CommandError
from backend.models import Game
from django.utils import timezone
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Finishes game'
    CONTRACT_NAME = 'UnilotPrizeCalculator'

    def handle(self, *args, **options):
        try:
            games = Game.objects.filter(status=Game.STATUS_PUBLISHED, ending_at__lte=timezone.now()).all()

            for game in games:
                if game.smart_contract_id in (None, '', '0'):
                    continue

                try:
                    tx = game.finish()
                except Exception as e:
                    message = 'Game %d: %s' % (game.id, e)

                    logger.error(message)
                    print(message)

                    continue

                logger.info('Finish transaction submitted: %s' % (tx))
                print('For progress see tx: %s' % (tx))

        except Game.DoesNotExist:
            print('No games to proceed')
