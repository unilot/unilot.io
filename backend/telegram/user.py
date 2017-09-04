from pprint import pprint

from telegram.bot import Bot
from telegram.update import Update
from django.contrib.auth.models import User
from django.db.models import Q
from backend.models import UserTelegram, UserWallet
from backend.telegram.helpers.chat import help_text, help_description_text
from ethereum.utils.web3 import AppWeb3
from django.db import transaction
from django.utils.translation import ugettext as _


def check_user(bot, update):
    """
    :type bot: Bot
    :param bot:
    :type update: Update
    :param update:
    :return:
    """

    tUser = update.message.from_user

    try:
        ut = UserTelegram.objects.get(id=tUser.id)
        """
        :type ut: UserTelegram
        """
        bot.sendMessage(update.message.chat_id, text=help_text())
    except UserTelegram.DoesNotExist:
        with transaction.atomic():
            register(bot,update)


def register(bot, update):
    """
    :type bot: Bot
    :param bot:
    :type update: Update
    :param update:
    :return:
    """

    t_user = update.message.from_user
    mixed_username = '%d@%s.tg' % (t_user.id, t_user.username)

    username_vars = [
        t_user.username,
        t_user.id,
        mixed_username
    ]

    users = User.objects.filter(
        Q(username=username_vars[0]) | Q(username=username_vars[1]) | Q(username=username_vars[2]))

    if not users:
        username = t_user.username
    else:
        for user in users:
            if user.username == t_user.username:
                username_vars.remove(t_user.username)
            elif int(user.username) == t_user.id:
                username_vars.remove(t_user.id)
            elif user.username == mixed_username:
                username_vars.remove(mixed_username)

        if username_vars:
            username = username_vars[0]
        else:
            username = ""

    if not username:
        raise Exception()

    user = User(username=username, first_name=t_user.first_name, last_name=t_user.last_name)
    password = User.objects.make_random_password(8)

    user.set_password(password)

    user.save()
    ut = UserTelegram(id=t_user.id)
    ut.user = user
    ut.save()

    web3 = AppWeb3.get_web3()

    wallet_password = User.objects.make_random_password(16)

    eth_wallet = UserWallet(passphrase=wallet_password)
    eth_wallet.user = user

    eth_wallet.id = web3.personal.newAccount(wallet_password)

    eth_wallet.save()

    bot.sendMessage(update.message.chat_id, text=help_description_text())


def get_balance(bot, update):
    """
    :type bot: Bot
    :param bot:
    :type update: Update
    :param update:
    :return:
    """

    tUser = update.message.from_user
    ut = UserTelegram.objects.prefetch_related('user', 'user__wallet').get(id=tUser.id)
    """
    :type ut: UserTelegram
    """

    wallet = ut.user.wallet.get()

    web3 = AppWeb3.get_web3()

    balance = web3.fromWei(number=web3.eth.getBalance(wallet.id), unit="ether")

    bot.sendMessage(update.message.chat_id, text=_('Your balance is %f ether' % (balance) ))


def get_wallet(bot, update):
    """
        :type bot: Bot
        :param bot:
        :type update: Update
        :param update:
        :return:
        """

    tUser = update.message.from_user
    ut = UserTelegram.objects.prefetch_related('user', 'user__wallet').get(id=tUser.id)
    """
    :type ut: UserTelegram
    """

    wallet = ut.user.wallet.get()

    bot.sendMessage(update.message.chat_id,
                    text=_('Your wallet id is "%s". Transfer funds to improve your balance.' % (wallet.id)))
