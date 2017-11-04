from oauth2_provider.contrib.rest_framework import TokenHasScope
from rest_framework import generics
from rest_framework.response import Response
from web3.main import Web3

from backend.models import Game
from backend.serializers.game import PublicGameSerializer, GameWinner


class GamesView(generics.ListAPIView):
    permission_classes = [TokenHasScope]
    required_scopes = ['read']
    queryset = Game.filter_active()
    serializer_class = PublicGameSerializer


class SingleGameView(generics.RetrieveAPIView):
    permission_classes = [TokenHasScope]
    required_scopes = ['read']
    queryset = Game
    serializer_class = PublicGameSerializer


class GamePrizesView(generics.RetrieveAPIView):
    permission_classes = [TokenHasScope]
    required_scopes = ['read']
    queryset = Game
    serializer_class = GameWinner

    def retrieve(self, request, *args, **kwargs):
        game = self.get_object()

        prize_data = []

        if game.status in (Game.STATUS_PUBLISHED, Game.STATUS_FINISHING):
            i = 1
            for prize in game.calculate_prizes():
                prize_data.append({
                    'address': '0x0000000000000000000000000000000000000000',
                    'position': i,
                    'prize_amount': Web3.fromWei(prize, 'ether')
                })

                i += 1

        elif game.status == Game.STATUS_FINISHED:
            i = 1

            for address, prize in game.get_winners().items():
                prize_data.append({
                    'address': address,
                    'position': i,
                    'prize_amount': prize
                })

                i += 1

        serializer = GameWinner(prize_data, many=True)

        return Response(serializer.data)


class GameArchivedView(generics.ListAPIView):
    permission_classes = [TokenHasScope]
    required_scopes = ['read']
    queryset = Game.filter_archived()
    serializer_class = PublicGameSerializer
