from django.core.files.storage import default_storage

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from google.protobuf.json_format import MessageToDict

from .serializers import KeySerializer, ServiceKeyVersionSerializer
from configuration.settings import MEDIA_ROOT
from configs.models import Service, ServiceKey, ServiceVersion
from protobuf import data_pb2


class ConfigAPIView(APIView):
    def convert_is_used_to_bool(self, is_used):
        if is_used == 1:
            return False
        elif is_used == 2:
            return True
        elif is_used is None:
            return None
        else:
            return ValueError('incorrect is_used flag')

    def convert_protobuf_to_dict(self, request):
        file = request.data['file']
        with default_storage.open('tmp/data.bin', 'wb') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
                destination.close()
        path = MEDIA_ROOT + '/tmp/data.bin'
        f = open(path, 'rb')
        read_message = data_pb2.ConfigMessage()
        read_message.ParseFromString(f.read())
        return MessageToDict(read_message)

    def get(self, request):
        name = request.query_params.get('service', None)
        if name is None:
            serializer = ServiceKeyVersionSerializer(
                ServiceVersion.objects.all(), many=True
            )
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        version = request.query_params.get('version')
        if version and name:
            try:
                service = Service.objects.get(name=name)
                version = ServiceVersion.objects.get(
                    service=service, version=version
                )
                service_key_instance = ServiceKey.objects.filter(
                    service=service, version=version
                )
                serializer = KeySerializer(
                    instance=service_key_instance, many=True
                )
                return Response(
                    data=serializer.data, status=status.HTTP_200_OK
                )
            except KeyError:
                Response(
                    data='record not found', status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(data='incorrect query params')

    def post(self, request):
        dict_message = self.convert_protobuf_to_dict(request)
        try:
            name = dict_message['service']
        except KeyError:
            return Response(
                data='invalid service', status=status.HTTP_400_BAD_REQUEST
            )
        try:
            version = dict_message['version']
        except KeyError:
            return Response(
                data='no version in file', status=status.HTTP_400_BAD_REQUEST
            )
        try:
            is_used_integer = dict_message['isUsed']
            is_used = self.convert_is_used_to_bool(is_used_integer)
        except KeyError:
            return Response(
                data="can't find is_used flag",
                status=status.HTTP_400_BAD_REQUEST
            )
        serv_settings = dict_message['keys']
        try:
            service = Service.objects.get(name=name)
            if ServiceVersion.objects.filter(
                service=service, version=version
            ).exists():
                return Response(
                    data='config already exists',
                    status=status.HTTP_400_BAD_REQUEST
                )
            ver_created = ServiceVersion.objects.create(
                service=service, version=version, is_used=is_used
            )
            for setting in serv_settings:
                ServiceKey.objects.create(
                    service=service,
                    version=ver_created,
                    service_key=setting['serviceKey'],
                    service_value=setting['serviceValue']
                )
            return Response(data='created', status=status.HTTP_201_CREATED)
        except Exception:
            service = Service.objects.create(name=name)
            ver_created = ServiceVersion.objects.create(
                service=service, version=version, is_used=is_used
            )
            for setting in serv_settings:
                ServiceKey.objects.create(
                    service=service,
                    version=ver_created,
                    service_key=setting['serviceKey'],
                    service_value=setting['serviceValue']
                )
            return Response(data='created', status=status.HTTP_201_CREATED)

    def patch(self, request):
        dict_message = self.convert_protobuf_to_dict(request)
        try:
            name = dict_message['service']
        except KeyError:
            return Response(
                data='invalid service', status=status.HTTP_400_BAD_REQUEST
            )
        try:
            version = dict_message['version']
        except KeyError:
            return Response(
                data='no version in file', status=status.HTTP_400_BAD_REQUEST
            )
        serv_settings = dict_message['keys']
        try:
            service = Service.objects.get(name=name)
            versions = ServiceVersion.objects.filter(service=service)
            flag_version = False
            for ver in versions:
                if ver.version == version:
                    flag_version = True
            flag = False
            try:
                is_used_integer = dict_message['isUsed']
                is_used = self.convert_is_used_to_bool(is_used_integer)
                if not flag_version:
                    ServiceVersion.objects.create(
                        service=service,
                        version=version,
                        is_used=is_used
                    )
                    flag = True
                else:
                    serv_version = ServiceVersion.objects.get(
                        service=service,
                        version=version
                    )
                    if serv_version.is_used != is_used:
                        serv_version.is_used = is_used
                        serv_version.save()
                        flag = True
            except KeyError:
                if not flag_version:
                    ServiceVersion.objects.create(
                        service=service,
                        version=version
                    )
                    flag = True
            try:
                version_query = ServiceVersion.objects.get(
                    service=service, version=version
                )
            except Exception:
                version_query = ServiceVersion.objects.create(
                    service=service, version=version
                )
            for setting in serv_settings:
                try:
                    s_k_instance = ServiceKey.objects.get(
                        service=service,
                        version=version_query,
                        service_key=setting['serviceKey']
                    )
                    if s_k_instance.service_value != setting['serviceValue']:
                        s_k_instance.service_value = setting['serviceValue']
                        s_k_instance.save()
                        flag = True
                except Exception:
                    ServiceKey.objects.create(
                        service=service,
                        version=version_query,
                        service_key=setting['serviceKey'],
                        service_value=setting['serviceValue']
                    )
                    flag = True
            if flag:
                return Response(
                    data='changed', status=status.HTTP_206_PARTIAL_CONTENT
                )
            return Response(
                data='no changes', status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return Response(
                data='record does not exist',
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request):
        name = request.query_params.get('service')
        version = request.query_params.get('version')
        try:
            service = Service.objects.get(name=name)
            service_version = ServiceVersion.objects.get(
                service=service, version=version
            )
            if service_version.is_used:
                return Response(
                    data='config is in use',
                    status=status.HTTP_400_BAD_REQUEST
                )
            service_version.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(
                data='no record', status=status.HTTP_400_BAD_REQUEST
            )

    def put(self, request):
        dict_message = self.convert_protobuf_to_dict(request)
        try:
            name = dict_message['service']
        except KeyError:
            return Response(
                data='invalid service', status=status.HTTP_400_BAD_REQUEST
            )
        try:
            version = dict_message['version']
        except KeyError:
            return Response(
                data='no version in file', status=status.HTTP_400_BAD_REQUEST
            )
        try:
            is_used_integer = dict_message['isUsed']
            is_used = self.convert_is_used_to_bool(is_used_integer)
        except KeyError:
            return Response(
                data="can't find is_used flag",
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            serv_settings = dict_message['keys']
        except KeyError:
            return Response(data='no keys', status=status.HTTP_400_BAD_REQUEST)
        service, service_created = Service.objects.get_or_create(name=name)
        flag = False
        if service_created:
            flag = True
        try:
            version_query = ServiceVersion.objects.get(
                service=service, version=version
            )
            if version_query.is_used != is_used:
                version_query.is_used = is_used
                version_query.save()
                flag = True
        except Exception:
            version_query = ServiceVersion.objects.create(
                service=service, version=version, is_used=is_used
            )
            flag = True
        for setting in serv_settings:
            try:
                service_key_instance = ServiceKey.objects.get(
                    service=service,
                    version=version_query,
                    service_key=setting['serviceKey']
                )
                if service_key_instance.service_value != \
                        setting['serviceValue']:
                    service_key_instance.service_value = \
                        setting['serviceValue']
                    service_key_instance.save()
                    flag = True
            except Exception:
                ServiceKey.objects.create(
                    service=service,
                    version=version_query,
                    service_key=setting['serviceKey'],
                    service_value=setting['serviceValue']
                )
                flag = True
        if flag:
            return Response(data='put', status=status.HTTP_201_CREATED)
        return Response(data='no changes', status=status.HTTP_400_BAD_REQUEST)
