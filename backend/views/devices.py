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
    #
    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #
    #     send_result_dict = serializer.send()
    #
    #     headers = self.get_success_headers(serializer.data)
    #
    #     return response.Response(serializer.data, status=status.HTTP_200_OK, headers=headers)


