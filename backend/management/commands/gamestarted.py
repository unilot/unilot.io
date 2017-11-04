import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from backend.models import Game
from backend.serializers import push
from backend.utils.push import PushHelper

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Finishes game'
    CONTRACT_NAME = 'UnilotPrizeCalculator'

    def handle(self, *args, **options):
        try:
            games = Game.objects.filter(
                status=Game.STATUS_PUBLISHED,
                type=Game.TYPE_1_DAY,
                ending_at__gte=timezone.now()).all()

            for game in games:
                gcm_push_message = push.GameStartedPushMessage(payload=game, is_localized=True)
                apns_push_message = push.GameStartedPushMessage(payload=game, is_localized=False)

                PushHelper.inform_all_devices(gcm_push_message, apns_push_message)

        except Game.DoesNotExist:
            print('No games to proceed')
