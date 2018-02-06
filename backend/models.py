from collections import OrderedDict

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _
from martor.models import MartorField
from push_notifications.models import APNSDevice, GCMDevice
from web3.contract import Contract
from web3.main import Web3

from backend.serializers import push
from backend.utils.push import PushHelper
from ethereum.utils.web3 import AppWeb3, ContractHelper, AccountHelper
from web3.utils.compat import socket
from unilot import settings
from hvad.models import TranslatableModel, TranslatedFields


class Game(models.Model):
    STATUS_NEW       = 0
    STATUS_PUBLISHED = 10
    STATUS_FINISHING = 15
    STATUS_CANCELED  = 20
    STATUS_FINISHED  = 30

    TYPE_1_DAY   = 10
    TYPE_7_DAYS  = 30
    TYPE_30_DAYS = 50
    TOKEN_GAME = 70

    STATUS_LIST = (
        (STATUS_NEW, _('New')),
        (STATUS_PUBLISHED, _('Published (Still can buy a ticket)')),
        (STATUS_FINISHING, _('Finishing (Winner choosing in progress)')),
        (STATUS_CANCELED, _('Canceled (no winner)')),
        (STATUS_FINISHED, _('Finished (has winner)')),
    )

    TYPE_LIST = (
        (TYPE_1_DAY, _('1 day')),
        (TYPE_7_DAYS, _('7 days')),
        (TYPE_30_DAYS, _('30 days')),
        (TOKEN_GAME, _('Token game')),
    )

    CONTRACT_STATUS_MAP = {
        '0': STATUS_PUBLISHED,
        '1': STATUS_FINISHED,
        '3': STATUS_CANCELED
    }

    CONTRACT_NAME='UnilotTailEther'

    type = models.IntegerField(choices=TYPE_LIST, null=False)
    status = models.IntegerField(choices=STATUS_LIST, null=False, default=STATUS_NEW)
    smart_contract_id = models.CharField(max_length=42, null=False)
    transaction_id = models.CharField(max_length=66, null=False)
    prize_amount = models.FloatField(null=True, default=0)
    num_players = models.IntegerField(null=True, default=0)
    user = models.ForeignKey(User, null=True, on_delete=models.deletion.PROTECT, related_name='game')
    bet_amount = models.FloatField(null=False, default=0.01)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField()
    ending_at = models.DateTimeField()

    __web3__ = None

    def get_web3(self):
        if not self.__web3__:
            self.__web3__ = AppWeb3.get_web3()

        return self.__web3__

    def get_smart_contract(self):
        """
        :rtype: Contract
        """

        web3 = self.get_web3()
        contract = web3.eth.contract(contract_name=self.CONTRACT_NAME,
                                     abi=ContractHelper.get_abi(self.CONTRACT_NAME),
                                     address=self.smart_contract_id)

        return contract

    def add_bet_tracking(self, new_event=True, past_event=False):
        def update_game_stats(event_log):
            web3 = self.get_web3()

            args = event_log.get('args', {})

            num_players = args.get('numPlayers', 0)

            if num_players > self.num_players:
                self.num_players = num_players
                self.prize_amount = web3.fromWei(args.get('prizeAmount', 0), 'ether')

                self.save()

                push_message = push.GameUpdatedPushMessage(payload=self)

                PushHelper.inform_all_devices(push_message)

        contract = self.get_smart_contract()

        if new_event:
            transfer_filter = contract.on('NewPlayerAdded',
                                          filter_params={'address': self.smart_contract_id})
            transfer_filter.watch(update_game_stats)

        if past_event:
            transfer_filter = contract.pastEvents('NewPlayerAdded',
                                                  filter_params={'address': self.smart_contract_id})
            transfer_filter.watch(update_game_stats)

    def build_contract(self):
        web3 = self.get_web3()

        contract = web3.eth.contract(abi=ContractHelper.get_abi(self.CONTRACT_NAME),
                                     bytecode=ContractHelper.get_bytecode(self.CONTRACT_NAME),
                                     contract_name=self.CONTRACT_NAME)
        """
        :rtype contract: Contract
        """

        AccountHelper.unlock_base_account()



        def get_contract_address(event_log):
            """
            :param event_log:
            :type dict:
            :return:
            """

            if self.smart_contract_id in (None, '0'):
                self.smart_contract_id = event_log['address']

            if self.status == self.STATUS_NEW:
                self.status = self.STATUS_PUBLISHED

            self.save()

            self.add_bet_tracking()

        transfer_filter = contract.on('GameStarted')
        transfer_filter.watch(get_contract_address)

        # TODO move prices to config
        self.transaction_id = contract.deploy(
            transaction={'from': AccountHelper.get_base_account(), "gasPrice": ContractHelper.getGasPrice()},
            args=[web3.toWei(self.bet_amount, 'ether'), ContractHelper.getCalculatorContractAddress()])

    def finish(self):
        if not Web3.isAddress(self.smart_contract_id):
            raise AttributeError('Invalid smart contract address')

        if self.status != Game.STATUS_PUBLISHED:
            raise RuntimeError('Invalid status')

        num_players = self.get_stat().get('numPlayers', 0)

        if num_players < 5:
            self.ending_at += timezone.timedelta(hours=24)
            self.save()

            push_message = push.GameUpdatedPushMessage(payload=self)

            PushHelper.inform_all_devices(push_message)

            return None

        self.status = Game.STATUS_FINISHING
        self.ending_at += timezone.timedelta(hours=1)

        keep_trying = True

        while keep_trying:
            try:
                AccountHelper.unlock_base_account()
                keep_trying = False
            except socket.timeout:
                keep_trying = True

        keep_trying = True

        while keep_trying:
            try:
                contract = self.get_smart_contract()
                tx = contract.transact(transaction={'from': AccountHelper.get_base_account(),
                                                    'gasPrice': ContractHelper.getGasPrice()}).finish()
                keep_trying = False
            except socket.timeout:
                keep_trying = True

        self.save()

        push_message = push.GameUnpublishedPushMessage(payload=self)

        PushHelper.inform_all_devices(push_message)

        return tx

    def revoke(self):
        if not Web3.isAddress(self.smart_contract_id):
            raise AttributeError('Invalid smart contract address')

        if self.status != Game.STATUS_PUBLISHED:
            raise RuntimeError('Invalid status')

        self.status = Game.STATUS_CANCELED

        contract = self.get_smart_contract()

        AccountHelper.unlock_base_account()

        tx = contract.transact(transaction={'from': AccountHelper.get_base_account(),
                                            'gasPrice': ContractHelper.getGasPrice()}).revoke()

        self.save()

        return tx

    def get_winners(self):
        """
        :rtype: dict
        """
        if not Web3.isAddress(self.smart_contract_id):
            return []

        contract = self.get_smart_contract()
        winners, prizes = contract.call().getWinners()
        result = {}

        #Setting address
        for i, winner in enumerate([w_player.lower() for w_player in winners]):
            result[winner] = Web3.fromWei(prizes[i], 'ether')

        return OrderedDict(reversed(sorted(result.items(), key=lambda t: t[1])))

    def get_players(self):
        if self.smart_contract_id in (None, '0'):
            raise AttributeError('Smart contract id can not be empty')

        contract = self.get_smart_contract()

        return contract.call().getPlayers()


    def get_stat(self):
        contract = self.get_smart_contract()

        num_players, prize_amount, num_winners = contract.call().getStat()

        return {
            'numPlayers': num_players,
            'prizeAmount': prize_amount,
            'numWinners': num_winners
        }

    def get_state(self):
        contract = self.get_smart_contract()

        state = contract.call().getState()

        result = self.CONTRACT_STATUS_MAP.get(str(state))

        if result is None:
            result = self.status

        return result

    def calculate_prizes(self):
        """
        :rtype: list
        """

        if not Web3.isAddress(self.smart_contract_id):
            return []

        contract = self.get_smart_contract()

        return contract.call().calcaultePrizes()


    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        if not self.transaction_id or self.transaction_id == '0':
            self.build_contract()

        super(Game, self).save(force_insert=force_insert, force_update=force_update, using=using,
                               update_fields=update_fields)

    @classmethod
    def filter_active(cls):
        return cls.objects\
        .filter( started_at__lte=timezone.now(),
                 ending_at__gt=timezone.now(),
                 status__in=(Game.STATUS_PUBLISHED, Game.STATUS_FINISHING) )\
        .exclude(smart_contract_id__in=('', '0'))

    @classmethod
    def filter_archived(cls):
        return cls.objects\
        .filter( started_at__lte=timezone.now() )\
        .exclude(smart_contract_id__in=('', '0'), status=Game.STATUS_NEW)

    def __str__(self):
        return '%d - %s' % (self.id, ( self.smart_contract_id if self.smart_contract_id else '%s in progress' % self.transaction_id ) )


class UserTelegram(models.Model):
    user = models.ForeignKey(User, on_delete=models.deletion.PROTECT, related_name='telegram')
    id = models.IntegerField(primary_key=True)


class ExchangeRate(models.Model):
    C_CURRENCY_ETH = 10
    C_CURRENCY_BTC = 20

    CURRENCY_USD = 30

    CURRENCY_LIST = (
        (C_CURRENCY_ETH, _('ETH')),
        (C_CURRENCY_BTC, _('BTC')),
        (CURRENCY_USD, _('USD'))
    )

    base_currency = models.IntegerField(null = False, choices=CURRENCY_LIST)
    currency = models.IntegerField(null=False, choices=CURRENCY_LIST)
    rate = models.FloatField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)


class DeviceSettings(models.Model):
    language = models.CharField(choices=settings.LANGUAGES, max_length=2)
    dayly_game_notifications_enabled = models.BooleanField(default=True)
    weekly_game_notifications_enabled = models.BooleanField(default=True)
    bonus_game_notifications_enabled = models.BooleanField(default=True)
    apns_device = models.OneToOneField(to=APNSDevice, on_delete=models.deletion.CASCADE,
                                    related_name='settings_apns_device', null=True)
    gcm_device = models.OneToOneField(to=GCMDevice, on_delete=models.deletion.CASCADE,
                                    related_name='settings_gcm_device', null=True)


class FAQ(TranslatableModel):
    translations = TranslatedFields(
        question=models.CharField(max_length=255, null=False),
        answer = MartorField(null=False)
    )

    @property
    def question_(self):
        return self.question
