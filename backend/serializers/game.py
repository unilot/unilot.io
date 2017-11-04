from rest_framework import serializers
from web3.main import Web3

from backend.models import Game, ExchangeRate


class FiatExchangeCalculatorMixin():
    def convert_amount_to_fiat(self, obj, attribute_name='prize_amount'):
        """
        :param obj:
        :type obj: Game|dict
        :return: float
        """

        if type(obj) is dict:
            amount = float(obj[attribute_name])
        else:
            amount = float(getattr(obj, attribute_name, 0))

        if amount <= 0:
            return 0

        latest_exchange_rate = ExchangeRate.objects.order_by('-created_at').first()
        """
        :var latest_exchange_rate:
        :type latest_exchange_rate: ExchangeRate
        """

        return (amount * float(latest_exchange_rate.rate))

class PublicGameSerializer(serializers.ModelSerializer, FiatExchangeCalculatorMixin):
    __stat__ = None
    """
    :var __stats__:
    :type dict:
    """

    prize_amount_fiat = serializers.SerializerMethodField(method_name='convert_amount_to_fiat')
    bet_amount_fiat = serializers.SerializerMethodField()
    num_players = serializers.SerializerMethodField()
    prize_amount = serializers.SerializerMethodField()

    def __get_stat__(self, game):
        if self.__stat__ is None:
            self.__stat__ = {}

        if self.__stat__.get('g%d' % (game.id), None) is None:
            self.__stat__['g%d' % (game.id)] = game.get_stat()

        return self.__stat__

    def get_num_players(self, obj):
        try:
            stat = self.__get_stat__(obj)
        except:
            stat = {}

        return stat.get('numPlayers', getattr(obj, 'num_players'))

    def get_prize_amount(self, obj):
        stat = self.__get_stat__(obj)
        result = 0

        try:
            result = stat.get('prizeAmount')
        except:
            pass

        if result > 0:
            result = Web3.fromWei(result, 'ether')
        else:
            result = getattr(obj, 'prize_amount')

        return result

    def get_bet_amount_fiat(self, obj):
        return self.convert_amount_to_fiat(obj, attribute_name='bet_amount')

    class Meta:
        model = Game
        fields = ('id', 'status', 'type', 'smart_contract_id', 'prize_amount', 'prize_amount_fiat', 'num_players', 'bet_amount', 'bet_amount_fiat', 'started_at', 'ending_at')


class GameWinner(serializers.Serializer, FiatExchangeCalculatorMixin):
    address = serializers.CharField()
    position = serializers.IntegerField()
    prize_amount = serializers.FloatField()
    prize_amount_fiat = serializers.SerializerMethodField(method_name='convert_amount_to_fiat')
