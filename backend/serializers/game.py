from rest_framework import serializers
from backend.models import Game


class PublicGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('id', 'status', 'type', 'smart_contract_id', 'started_at', 'ending_at')