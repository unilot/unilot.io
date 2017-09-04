from telegram.bot import Bot
from telegram.update import Update
from backend.models import Game
from pprint import pprint

game_create = False

def create_start(bot, update):
    """
    :type bot: Bot
    :param bot:
    :type update: Update
    :param update:
    :return:
    """
    game_create = True


def get_list():
    for game in Game.objects.filter(status__in=[Game.STATUS_NEW, Game.STATUS_PUBLISHED]):
        pass
