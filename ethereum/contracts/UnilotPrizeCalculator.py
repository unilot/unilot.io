from ..utils.web3 import ContractHelper, AppWeb3
from unilot import settings


class UnilotPrizeCalculator():
    address = 0
    CONTRACT_NAME='UnilotPrizeCalculator'
    contract = None

    def __init__(self):
        self.address =  settings.WEB3_CONFIG.get('CALCULATOR_CONTRACT_ADDRESS')
        web3 = AppWeb3.get_web3()

        self.contract = web3.eth.contract(contract_name=self.CONTRACT_NAME,
                                     abi=ContractHelper.get_abi(self.CONTRACT_NAME),
                                     address=self.address)

    def get_prize_amount(self, total_amount):
        return self.contract.call().getPrizeAmount(total_amount)

    def get_num_winners(self, num_players):
        return self.contract.call().getNumWinners(num_players)

    def calculate_prizes(self, bet, num_players):
        return self.contract.call().calcaultePrizes(bet, num_players)

    def formula(self, x):
        return self.contract.call().formula(x)

    def calculate_step(self, num_winners):
        return self.contract.call().calculateStep(num_winners)
