from telegram.ext import CommandHandler, MessageHandler, Filters
from django_telegrambot.apps import DjangoTelegramBot
from telegram.bot import Bot
from telegram.update import Update
from backend.telegram import user
from pprint import pprint

from backend.telegram.helpers.chat import help_text


def start(bot, update):
    """
    :type bot: Bot
    :param bot:
    :type update: Update
    :param update:
    :return:
    """
    pprint('%d: %s' % (update.message.from_user.id, update.message.from_user.username))
    bot.sendMessage(update.message.chat_id, text='Hi!')


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text=help_text())


def main():
    dp = DjangoTelegramBot.dispatcher

    # User handlers
    dp.add_handler(CommandHandler('start', user.check_user)) # This probably should be refactored
    dp.add_handler(CommandHandler('get_balance', user.get_balance))
    dp.add_handler(CommandHandler('get_wallet', user.get_wallet))

    dp.add_handler(MessageHandler([Filters.text], help))

if __name__ == '__main__':
    main()
