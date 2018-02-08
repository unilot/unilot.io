from django.core.management.base import BaseCommand, CommandError
from push_notifications.models import GCMDevice, APNSDevice

from backend.models import Game
import logging

from backend.serializers import push
from backend.utils.push import PushHelper

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send push for game'

    def add_arguments(self, parser):
        parser.add_argument('game_id')
        parser.add_argument('game_type')
        parser.add_argument('device_token', type=str, nargs='?', default='')

    def handle(self, *args, **options):
        game_id = options.get('game_id')
        push_type = options.get('game_type')
        device_token = options.get('device_token')

        try:
            game = Game.objects.get(id=game_id)
            push_message = None

            if push_type == 'game_started':
                push_message = push.GameStartedPushMessage(payload=game)
            elif push_type == 'game_updated':
                push_message = push.GameNewPlayerPushMessage(payload=game)

            if push_message:
                if device_token and GCMDevice.objects.filter(registration_id=device_token).exists():
                    PushHelper.inform_gcm_devices(push_message, device_token)
                elif device_token and APNSDevice.objects.filter(registration_id=device_token).exists():
                    PushHelper.inform_apns_devices(push_message, device_token)
                else:
                    PushHelper.inform_all_devices(push_message)

        except Game.DoesNotExist:
            print('No games to proceed')
