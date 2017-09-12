from rest_framework import serializers
from backend.models import Device


class CreateDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('os', 'token')
