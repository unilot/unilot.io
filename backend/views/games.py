from django.http.response import HttpResponseBadRequest
from oauth2_provider.contrib.rest_framework import TokenHasScope
from rest_framework import generics, status
from rest_framework.response import Response
from web3.main import Web3

from backend.models import Game, GamePlayers
from backend.serializers.device import DeviceOS
from backend.serializers.game import PublicGameSerializer, GameWinner, GameDebugPush
from backend.utils.push import PushHelper


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
                    'prize_amount': {
                        'amount': Web3.fromWei(prize, 'ether'),
                        'currency': 'ETH'
                    }
                })

                i += 1

        elif game.status == Game.STATUS_FINISHED:
            i = 1

            for address, prize in game.get_winners().items():
                prize_data.append({
                    'address': address,
                    'position': i,
                    'prize_amount': {
                        'amount': prize,
                        'currency': 'ETH'
                    }
                })

                i += 1

        serializer = GameWinner(prize_data, many=True)

        return Response(serializer.data)


class GameArchivedView(generics.ListAPIView):
    permission_classes = [TokenHasScope]
    required_scopes = ['read']
    queryset = Game.filter_archived().order_by('-ending_at')
    serializer_class = PublicGameSerializer


class GameDebugPushView(generics.CreateAPIView):
    permission_classes = []
    required_scopes = ['read']
    queryset = Game.objects.filter()
    serializer_class = GameDebugPush

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()

        valid_data = serializer.validated_data
        action = valid_data.get('action')
        os = valid_data.get('os')
        token = valid_data.get('token')

        push_message = serializer.get_push_message(action, instance)

        if not push_message.is_valid():
            raise HttpResponseBadRequest(push_message.errors)

        if os is not None:
            if os == DeviceOS.IOS:
                PushHelper.inform_apns_devices(push_message, token)
            elif os == DeviceOS.ANDROID:
                PushHelper.inform_gcm_devices(push_message, token)
        else:
            PushHelper.inform_all_devices(push_message)

        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)


class BonusGamePlayersListView(generics.RetrieveAPIView):
    permission_classes = [ TokenHasScope ]
    required_scopes = ['read']
    queryset = Game.objects.filter(type__in=(Game.TYPE_30_DAYS, Game.TOKEN_GAME,))

    def get(self, request, *args, **kwargs):
        game = self.get_object() #Throws 404 on none-existing game

        players = GamePlayers.objects\
            .values('wallet')\
            .distinct('wallet')\
            .exclude(game__type__in=(Game.TYPE_30_DAYS, Game.TOKEN_GAME,))\
            .filter(game__started_at__gte=game.started_at, game__ending_at__lte=game.ending_at)

        return Response((player.get('wallet') for player in players), status=status.HTTP_200_OK)
