from configs.models import ServiceKey, Service, ServiceVersion
from rest_framework import serializers


class KeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceKey
        fields = ['service_key', 'service_value']

    def to_representation(self, instance):
        return {instance.service_key: instance.service_value}


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['name', ]


class ServiceVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceVersion
        fields = ['version', 'is_used']


class ServiceKeyVersionSerializer(serializers.ModelSerializer):
    service = serializers.SerializerMethodField()
    # version = serializers.SerializerMethodField()
    keys = serializers.SerializerMethodField()

    class Meta:
        model = ServiceVersion
        fields = ['service', 'version', 'is_used', 'keys']

    def get_service(self, obj):
        service = Service.objects.get(id=obj.service_id)
        return ServiceSerializer(service).data

    # def get_version(self, obj):
    #     service_version = ServiceVersion.objects.get(id=obj.version_id)
    #     return ServiceVersionSerializer(service_version).data

    def get_keys(self, obj):
        
        keys = ServiceKey.objects.filter(
            service_id=obj.service_id, version_id=obj.id
        )
        return KeySerializer(keys, many=True).data
