from decimal import Decimal
from rest_framework import serializers
from backend.models import Game, ExchangeRate


class PublicGameSerializer(serializers.ModelSerializer):
    prize_amount_fiat = serializers.SerializerMethodField(method_name='convert_prize_amount_to_fiat')

    def convert_prize_amount_to_fiat(self, obj):
        """
        :param obj:
        :type obj: Game
        :return: float
        """

        latest_exchange_rate = ExchangeRate.objects.order_by('-created_at').first()
        """
        :var latest_exchange_rate:
        :type latest_exchange_rate: ExchangeRate
        """

        return float(Decimal(obj.prize_amount) * Decimal(latest_exchange_rate.rate))


    class Meta:
        model = Game
        fields = ('id', 'status', 'type', 'smart_contract_id', 'prize_amount', 'prize_amount_fiat', 'num_players', 'started_at', 'ending_at')
