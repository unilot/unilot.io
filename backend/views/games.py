from oauth2_provider.contrib.rest_framework import TokenHasScope
from random import randint
from rest_framework import generics
from rest_framework.response import Response

from backend.models import Game
from backend.serializers.game import PublicGameSerializer, GameWinner


class GamesView(generics.ListAPIView):
    permission_classes = [TokenHasScope]
    required_scopes = ['read']
    queryset = Game.filter_active()
    serializer_class = PublicGameSerializer

class GamePrizesView(generics.RetrieveAPIView):
    permission_classes = [TokenHasScope]
    required_scopes = ['read']
    queryset = Game
    serializer_class = GameWinner

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        num_prizes = randint(0,9)

        prize_data = []
        total_prize = instance.prize_amount
        prize = total_prize/2

        for i in range(0, num_prizes):
            player_data = {
                'address': '0x0000000000000000000000000000000000000000',
                'position': i+1,
                'prize_amount': prize
            }

            prize /= 2

            prize_data.append(player_data)

        serializer = GameWinner(prize_data, many=True)

        return Response(serializer.data)
