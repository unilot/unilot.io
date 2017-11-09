from django.http.response import HttpResponseBadRequest
from oauth2_provider.contrib.rest_framework import TokenHasScope
from rest_framework import generics, status
from rest_framework.response import Response
from web3.main import Web3

from backend.models import Game
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


class GameDebugPushView(generics.CreateAPIView):
    permission_classes = [TokenHasScope]
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
