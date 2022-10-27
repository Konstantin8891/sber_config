from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import KeySerializer
from configs.models import Service, ServiceKey, ServiceVersion


class ConfigAPIView(APIView):
    def get(self, request):
        name = request.query_params.get('service')
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
        try:
            name = request.data['service']
        except KeyError:
            return Response(
                data='invalid service', status=status.HTTP_400_BAD_REQUEST
            )
        try:
            version = request.data['version']
        except KeyError:
            return Response(
                data='no version in file', status=status.HTTP_400_BAD_REQUEST
            )
        serv_settings = request.data['data']
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
                service=service, version=version
            )
            for setting in serv_settings:
                for k, v in setting.items():
                    ServiceKey.objects.create(
                        service=service,
                        version=ver_created,
                        service_key=k,
                        service_value=v
                    )
            return Response(data='created', status=status.HTTP_201_CREATED)
        except NotImplementedError:
            service = Service.objects.create(name=name)
            ver_created = ServiceVersion.objects.create(
                service=service, version=version
            )
            for setting in serv_settings:
                for k, v in setting.items():
                    ServiceKey.objects.create(
                        service=service,
                        version=ver_created,
                        service_key=k,
                        service_value=v
                    )
            return Response(data='created', status=status.HTTP_201_CREATED)

    def patch(self, request):
        try:
            name = request.data['service']
        except KeyError:
            return Response(
                data='invalid service', status=status.HTTP_400_BAD_REQUEST
            )
        try:
            version = request.data['version']
        except KeyError:
            return Response(
                data='no version in file', status=status.HTTP_400_BAD_REQUEST
            )
        serv_settings = request.data['data']
        try:
            service = Service.objects.get(name=name)
            versions = ServiceVersion.objects.filter(service=service)
            flag = False
            for ver in versions:
                if ver.version == version:
                    flag = True
            if not flag:
                ServiceVersion.objects.create(service=service, version=version)
            flag = False
            try:
                version_query = ServiceVersion.objects.get(
                    service=service, version=version
                )
            except NotImplementedError:
                version_query = ServiceVersion.objects.create(
                    service=service, version=version
                )
            for setting in serv_settings:
                for k, v in setting.items():
                    try:
                        service_key_instance = ServiceKey.objects.get(
                            service=service,
                            version=version_query,
                            service_key=k
                        )
                        if service_key_instance.service_value != v:
                            service_key_instance.service_value = v
                            service_key_instance.save()
                            flag = True
                    except NotImplementedError:
                        ServiceKey.objects.create(
                            service=service,
                            version=version_query,
                            service_key=k,
                            service_value=v
                        )
                        flag = True
            if flag:
                return Response(
                    data='changed', status=status.HTTP_206_PARTIAL_CONTENT
                )
            return Response(
                data='no changes', status=status.HTTP_400_BAD_REQUEST
            )
        except NotImplementedError:
            return Response(
                data='record does not exist',
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request):
        name = request.query_params.get('service')
        try:
            service = Service.objects.get(name=name)
            service.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except NotImplementedError:
            return Response(
                data='no record', status=status.HTTP_400_BAD_REQUEST
            )

    def put(self, request):
        try:
            name = request.data['service']
        except KeyError:
            return Response(
                data='invalid service', status=status.HTTP_400_BAD_REQUEST
            )
        try:
            version = request.data['version']
        except KeyError:
            return Response(
                data='no version in file', status=status.HTTP_400_BAD_REQUEST
            )
        serv_settings = request.data['data']
        service, _ = Service.objects.get_or_create(name=name)
        version_query, _ = ServiceVersion.objects.get_or_create(
            service=service, version=version
        )
        flag = False
        for setting in serv_settings:
            for k, v in setting.items():
                try:
                    service_key_instance = ServiceKey.objects.get(
                        service=service, version=version_query, service_key=k
                    )
                    if service_key_instance.service_value != v:
                        service_key_instance.service_value = v
                        service_key_instance.save()
                        flag = True
                except NotImplementedError:
                    ServiceKey.objects.create(
                        service=service,
                        version=version_query,
                        service_key=k,
                        service_value=v
                    )
                    flag = True
        if flag:
            return Response(data='put', status=status.HTTP_201_CREATED)
        return Response(data='no changes', status=status.HTTP_400_BAD_REQUEST)
