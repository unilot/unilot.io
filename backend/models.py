from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext as _
from web3.contract import Contract

from ethereum.utils.web3 import AppWeb3, ContractHelper, AccountHelper, get_config


class Game(models.Model):
    STATUS_NEW = 0
    STATUS_PUBLISHED = 10
    STATUS_CANCELED = 20
    STATUS_FINISHED = 30

    TYPE_1_DAY = 10
    TYPE_7_DAYS = 30
    TYPE_30_DAYS = 50

    STATUS_LIST = (
        (STATUS_NEW, _('New')),
        (STATUS_PUBLISHED, _('Published (Still can buy a ticket)')),
        (STATUS_CANCELED, _('Canceled (no winner)')),
        (STATUS_FINISHED, _('Finished (has winner)')),
    )

    TYPE_LIST = (
        (TYPE_1_DAY, _('1 day')),
        (TYPE_7_DAYS, _('7 days')),
        (TYPE_7_DAYS, _('30 days')),
    )

    TYPE_BET_MAP = {
        TYPE_1_DAY: 0.05,
        TYPE_7_DAYS: 0.05,
    }

    CONTRACT_NAME='UnilotEther'

    type = models.IntegerField(choices=TYPE_LIST, null=False)
    status = models.IntegerField(choices=STATUS_LIST, null=False, default=STATUS_NEW)
    smart_contract_id = models.CharField(max_length=42, null=False)
    transaction_id = models.CharField(max_length=66, null=False)
    prize_amount = models.FloatField(null=True, default=0)
    num_players = models.IntegerField(null=True, default=0)
    user = models.ForeignKey(User, null=True, on_delete=models.deletion.PROTECT, related_name='game')
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

    def build_contract(self):
        web3 = self.get_web3()

        contract = web3.eth.contract(abi=ContractHelper.get_abi(self.CONTRACT_NAME),
                                     bytecode=ContractHelper.get_bytecode(self.CONTRACT_NAME),
                                     contract_name=self.CONTRACT_NAME)
        """
        :type contract: Contract
        """

        AccountHelper.unlock_base_account()

        def get_contract_address(event_log):
            """
            :param event_log:
            :type dict:
            :return:
            """

            self.smart_contract_id = event_log['address']
            self.status = self.STATUS_PUBLISHED
            self.save()

        transfer_filter = contract.on('GameStarted')
        transfer_filter.watch(get_contract_address)

        # TODO move prices to config
        self.transaction_id = contract.deploy(transaction={'from': AccountHelper.get_base_account(), "gasPrice": web3.toWei(25, 'gwei')},
                                              args=[web3.toWei(0.05, 'ether')])

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        if not self.transaction_id or self.transaction_id == '0':
            self.build_contract()

        super(Game, self).save(force_insert=force_insert, force_update=force_update, using=using,
                               update_fields=update_fields)

    @classmethod
    def filter_active(self):
        return self.objects\
        .filter( started_at__lte=timezone.now(), ending_at__gt=timezone.now(), status=Game.STATUS_PUBLISHED )\
        .exclude(smart_contract_id__in=('', '0'))

    def __str__(self):
        return '%d - %s' % (self.id, ( self.smart_contract_id if self.smart_contract_id else '%s in progress' % self.transaction_id ) )


class UserTelegram(models.Model):
    user = models.ForeignKey(User, on_delete=models.deletion.PROTECT, related_name='telegram')
    id = models.IntegerField(primary_key=True)

class Device(models.Model):
    OS_IOS = 10
    OS_ANDROID = 20

    OS_LIST = (
        (OS_IOS, _('IOS')),
        (OS_ANDROID, _('Android OS'))
    )

    os = models.IntegerField(choices=OS_LIST, null=False)
    token = models.CharField(max_length=1024)
    fail_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('os', 'token'))

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
