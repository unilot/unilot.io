from push_notifications.models import GCMDevice, APNSDevice


class PushHelper:
    @staticmethod
    def inform_all_devices(push_message):
        gcmDevices = GCMDevice.objects.filter()
        apnsDevices = APNSDevice.objects.filter()

        if push_message.is_valid():
            gcmDevices.send_message(message=None, extra=push_message.data, use_fcm_notifications=False)

            apnsDevices.send_message(message=push_message.data.get('message', {}).get('en'),
                                     extra=push_message.data, content_available=True,
                                     sound='chime.aiff')
