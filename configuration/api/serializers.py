from configs.models import ServiceKey
from rest_framework import serializers


class KeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceKey
        fields = ['service_key', 'service_value']

    def to_representation(self, instance):
        return {instance.service_key: instance.service_value}
