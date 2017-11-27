from django.db.models.query_utils import Q
from push_notifications.models import GCMDevice, APNSDevice
from unilot import settings


class PushHelper:
    @staticmethod
    def inform_all_devices(push_message):
        if push_message.is_valid():
            PushHelper.inform_gcm_devices(push_message)
            PushHelper.inform_apns_devices(push_message)

    @staticmethod
    def inform_apns_devices(push_message, token=None):
        prefix = 'settings_apns_device'
        filter_data = {'%s__%s' % (prefix, field_name):value
                       for field_name, value in push_message.get_required_settings().items()}
        legacy_filter_data = {prefix:None}

        for language_tuple in settings.LANGUAGES:
            language_code = language_tuple[0]
            filter_data['%s__language' % (prefix)] =  language_code

            if token is not None:
                tokens = list(token) if isinstance(token, (list, tuple)) else [token]
                filter_data['registration_id__in'] = tokens
                legacy_filter_data['registration_id__in'] = tokens

            if language_code == 'en':
                devices = APNSDevice.objects.filter(Q(**filter_data) | Q(**legacy_filter_data))
            else:
                devices = APNSDevice.objects.filter(Q(**filter_data))

            devices.send_message(message=push_message.data.get('message', {}).get(language_code),
                                 extra=push_message.data, content_available=True, mutable_content=True,
                                 sound='chime.aiff')

    @staticmethod
    def inform_gcm_devices(push_message, token=None):
        if token is None:
            devices = GCMDevice.objects.filter()
        elif isinstance(token, (list, tuple)):
            devices = GCMDevice.objects.filter(registration_id__in=token)
        else:
            devices = GCMDevice.objects.get(registration_id=token)

        devices.send_message(message=None, extra=push_message.data, use_fcm_notifications=False)
