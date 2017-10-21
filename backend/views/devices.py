from rest_framework import generics
from oauth2_provider.contrib.rest_framework import TokenHasScope
from backend.serializers.device import CreateDeviceSerializer


class DeviceCreateViewSet(generics.CreateAPIView):
    permission_classes = [TokenHasScope]
    required_scopes = ['read']
    serializer_class = CreateDeviceSerializer
