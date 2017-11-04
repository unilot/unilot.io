from push_notifications.models import GCMDevice, APNSDevice


class PushHelper:
    @staticmethod
    def inform_all_devices(gcm_push_message, apns_push_message):
        gcmDevices = GCMDevice.objects.filter()
        apnsDevices = APNSDevice.objects.filter()

        if gcm_push_message.is_valid():
            gcmDevices.send_message(message=None, extra=gcm_push_message.data)

        if apns_push_message.is_valid():
            apnsDevices.send_message(message=None, extra=apns_push_message.data)
