from rest_framework import generics, status, response
from oauth2_provider.contrib.rest_framework import TokenHasScope

from backend.serializers.device import CreateDeviceSerializer, DebugPush


class DeviceCreateView(generics.CreateAPIView):
    permission_classes = [TokenHasScope]
    required_scopes = ['read']
    serializer_class = CreateDeviceSerializer

class SendPushView(generics.CreateAPIView):
    permission_classes = [TokenHasScope]
    required_scopes = ['read']
    serializer_class = DebugPush
