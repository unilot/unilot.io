from rest_framework import serializers
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
    prize_amount_fiat = serializers.SerializerMethodField(method_name='convert_amount_to_fiat')
    bet_amount_fiat = serializers.SerializerMethodField()

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
