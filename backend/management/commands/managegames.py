from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from backend.models import Game
from django.contrib.auth.models import User
from django.utils.timezone import now

from ethereum.utils.web3 import AppWeb3


class Command(BaseCommand):
    help = 'Manages active games. Closes outdated, runs winner check, provides prizes, reopens games'

    def handle(self, *args, **options):
        checklist = []

        for type_data in Game.TYPE_LIST:
            type_index = type_data[0]
            checklist.append(type_index)

        for game in Game.objects.filter(status__in=[Game.STATUS_NEW, Game.STATUS_PUBLISHED]):
            checklist.remove(game.type)

            #TODO update game status depending on conditions

        if checklist:
            for type in checklist:
                starting_at = timezone.now()
                ending_at = starting_at + timezone.timedelta(hours=type)
                game = Game(
                    type=type, status=Game.STATUS_PUBLISHED, started_at=starting_at,
                    ending_at=ending_at)

                game.save()
