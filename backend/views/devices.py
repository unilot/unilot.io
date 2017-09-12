from rest_framework import viewsets, mixins
from oauth2_provider.contrib.rest_framework import TokenHasScope
from backend.serializers.device import CreateDeviceSerializer


class DeviceCreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [TokenHasScope]
    required_scopes = ['read']
    serializer_class = CreateDeviceSerializer
