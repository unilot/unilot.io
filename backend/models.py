from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from web3.contract import Contract

from ethereum.utils.web3 import AppWeb3, ContractHelper, AccountHelper


class Game(models.Model):
    STATUS_NEW = 0
    STATUS_PUBLISHED = 10
    STATUS_CANCELED = 20
    STATUS_FINISHED = 30

    TYPE_1_DAY = 10
    TYPE_7_DAYS = 30

    STATUS_LIST = (
        (STATUS_NEW, _('New')),
        (STATUS_PUBLISHED, _('Published (Still can buy a ticket)')),
        (STATUS_CANCELED, _('Canceled (no winner)')),
        (STATUS_FINISHED, _('Finished (has winner)')),
    )

    TYPE_LIST = (
        (TYPE_1_DAY, _('1 day')),
        (TYPE_7_DAYS, _('7 days')),
    )

    TYPE_BET_MAP = {
        TYPE_1_DAY: 0.05,
        TYPE_7_DAYS: 0.05,
    }

    CONTRACT_NAME='Lottery'

    type = models.IntegerField(choices=TYPE_LIST, null=False)
    status = models.IntegerField(choices=STATUS_LIST, null=False)
    smart_contract_id = models.CharField(max_length=42, null=False)
    transaction_id = models.CharField(max_length=66, null=False)
    user = models.ForeignKey(User, null=True, on_delete=models.deletion.PROTECT, related_name='game')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField()
    ending_at = models.DateTimeField()

    __web3__ = None

    def get_web3(self):
        if not self.__web3__:
            self.__web3__ = AppWeb3.get_web3();

        return self.__web3__

    def get_smart_contract(self):
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

        self.transaction_id = contract.deploy(transaction={"from": web3.eth.coinbase},
                                              args=[web3.toWei(self.TYPE_BET_MAP[self.type], 'ether')])
        self.smart_contract_id = contract.address

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):


        if not self.transaction_id:
            self.build_contract()


        super(Game, self).save(force_insert=force_insert, force_update=force_update, using=using,
                               update_fields=update_fields)


class UserTelegram(models.Model):
    user = models.ForeignKey(User, on_delete=models.deletion.PROTECT, related_name='telegram')
    id = models.IntegerField(primary_key=True)
