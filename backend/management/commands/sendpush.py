from django.core.management.base import BaseCommand, CommandError
from backend.models import Game
import logging

from backend.serializers import push
from backend.utils.push import PushHelper

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Finishes game'
    CONTRACT_NAME = 'UnilotPrizeCalculator'

    def handle(self, *args, **options):
        game_id = args[1]
        push_type = args[2]
        try:
            game = Game.objects.get(id=game_id)

            if push_type == 'game_started':
                push_message = push.GameStartedPushMessage(payload=game)
                PushHelper.inform_all_devices(push_message)

        except Game.DoesNotExist:
            print('No games to proceed')
