from decimal import Decimal
from rest_framework import serializers
from backend.models import Game, ExchangeRate

class FiatExchangeCalculatorMixin():
    def convert_amount_to_fiat(self, obj, attribute_name='prize_amount'):
        """
        :param obj:
        :type obj: Game
        :return: float
        """

        if type(obj) is not dict:
            data = dict((key, value) for (key,value) in obj.__class__.__dict__.items())
        else:
            data = obj

        amount = Decimal(data[attribute_name])

        if amount <= 0:
            return 0

        latest_exchange_rate = ExchangeRate.objects.order_by('-created_at').first()
        """
        :var latest_exchange_rate:
        :type latest_exchange_rate: ExchangeRate
        """

        return float(Decimal(data[attribute_name]) * Decimal(latest_exchange_rate.rate))

class PublicGameSerializer(serializers.ModelSerializer, FiatExchangeCalculatorMixin):
    prize_amount_fiat = serializers.SerializerMethodField(method_name='convert_amount_to_fiat')


    class Meta:
        model = Game
        fields = ('id', 'status', 'type', 'smart_contract_id', 'prize_amount', 'prize_amount_fiat', 'num_players', 'started_at', 'ending_at')


class GameWinner(serializers.Serializer, FiatExchangeCalculatorMixin):
    address = serializers.CharField()
    position = serializers.IntegerField()
    prize_amount = serializers.FloatField()
    prize_amount_fiat = serializers.SerializerMethodField(method_name='convert_amount_to_fiat')
