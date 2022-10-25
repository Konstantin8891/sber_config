from ensurepip import version
from configs.models import Service, ServiceKey
from rest_framework import serializers


class KeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceKey
        fields = ['service_key', 'service_value']
    
    def to_representation(self, instance):
        return {instance.service_key: instance.service_value}


class VersionsSerializer(serializers.ModelSerializer):
    key = KeySerializer(many=True)
    version = serializers.ReadOnlyField(source='serviceversion.version')

    class Meta:
        model = Service
        fields = ['key', 'version']