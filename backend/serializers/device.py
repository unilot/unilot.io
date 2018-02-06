from push_notifications.models import APNSDevice, GCMDevice
from rest_framework import serializers
from django.utils.translation import ugettext as _

from backend.models import DeviceSettings


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

    os = serializers.ChoiceField(choices=DeviceOS.CHOICES)
    token = serializers.CharField()

    def create(self, validated_data):
        device_data = {
            'registration_id': validated_data.get('token', None)
        }

        if validated_data.get('os') == 10:
            APNSDevice.objects.get_or_create(**device_data)
        else:
            device_data['cloud_message_type'] = 'FCM'
            GCMDevice.objects.get_or_create(**device_data)

        # Pretty dirty hack to keep back compatibility
        instance = DummyDeviceObject(**device_data)

        return instance


class CreateDeviceWithSettingsSerializer(serializers.ModelSerializer):
    os = serializers.ChoiceField(choices=DeviceOS.CHOICES, write_only=True)
    token = serializers.CharField(write_only=True)

    # def to_representation(self, instance):
    #     super(CreateDeviceWithSettingsSerializer, self).to_representation(instance)

    def create(self, validated_data):
        create_data = validated_data.copy()

        device_data = {
            'registration_id': create_data.pop('token', None)
        }
        os = create_data.pop('os', None)
        model_cls = self.Meta.model

        if os == 10:
            (device, device_is_created) = APNSDevice.objects.get_or_create(**device_data)
            create_data['apns_device'] = device
            (settings, settings_is_created) = model_cls.objects.update_or_create(defaults=create_data,
                                                          apns_device__registration_id=device.registration_id)
        else:
            device_data['cloud_message_type'] = 'FCM'
            (device, is_created) = GCMDevice.objects.get_or_create(**device_data)
            create_data['gcm_device'] = device
            (settings, settings_is_created) = model_cls.objects.update_or_create(defaults=create_data,
                                                          gcm_device__registration_id=device.registration_id)

        return settings

    class Meta:
        model = DeviceSettings
        fields = ('os', 'token', 'language', 'dayly_game_notifications_enabled', 'weekly_game_notifications_enabled',
                  'bonus_game_notifications_enabled', 'token_game_notifications_enabled')
