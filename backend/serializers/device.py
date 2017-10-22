from push_notifications.models import APNSDevice, GCMDevice
from rest_framework import serializers
from django.utils.translation import ugettext as _


class DeviceOS:
    IOS = 10
    ANDROID = 20

    LIST = (IOS, ANDROID)

    CHOICES = (
        (IOS, _('IOS')),
        (ANDROID, _('Android OS'))
    )


class DummyDeviceObject(object):
    def __init__(self, registration_id, cloud_message_type=None):
        self.os = DeviceOS.IOS if cloud_message_type is None else DeviceOS.ANDROID
        self.token = registration_id


class CreateDeviceSerializer(serializers.Serializer):

    os    = serializers.IntegerField()
    token = serializers.CharField()

    def create(self, validated_data):
        device_data = {
            'registration_id': validated_data.get('token', None)
        }

        if int(validated_data.get('os', '')) not in DeviceOS.LIST:
            raise AttributeError(('Invalid value "%s" of os field') % (validated_data.get('os')))

        if validated_data.get('os') == 10:
            APNSDevice.objects.create(**device_data)
        else:
            device_data['cloud_message_type'] = 'FCM'
            GCMDevice.objects.create(**device_data)

        # Pretty dirty hack to keep back compatibility
        instance = DummyDeviceObject(**device_data)

        return instance
