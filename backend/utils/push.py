from push_notifications.models import GCMDevice, APNSDevice


class PushHelper:
    @staticmethod
    def inform_all_devices(push_message):
        if push_message.is_valid():
            PushHelper.inform_gcm_devices(push_message)
            PushHelper.inform_apns_devices(push_message)

    @staticmethod
    def inform_apns_devices(push_message, token=None):
        if token is None:
            devices = APNSDevice.objects.filter()
        elif isinstance(token, (list, tuple)):
            devices = APNSDevice.objects.filter(registration_id__in=token)
        else:
            devices = APNSDevice.objects.get(registration_id=token)

        devices.send_message(message=None, extra=push_message.data, content_available=True,
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
