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
        try:
            is_used = request.data['is_used']
        except KeyError:
            return Response(
                data="can't find is_used flag",
                status=status.HTTP_400_BAD_REQUEST
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
                service=service, version=version, is_used=is_used
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
        except Exception:
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
        # try:
        #     is_used = request.data['is_used']
        # except Exception:
        #     pass
        serv_settings = request.data['data']
        try:
            service = Service.objects.get(name=name)
            versions = ServiceVersion.objects.filter(service=service)
            flag_version = False
            for ver in versions:
                if ver.version == version:
                    flag_version = True
            flag = False
            try:
                is_used = request.data['is_used']
                print(is_used)
                print(flag_version)
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
                    except Exception:
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
            print(service)
            service_version = ServiceVersion.objects.get(
                service=service, version=version
            )
            print(service_version)
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
        try:
            is_used = request.data['is_used']
        except KeyError:
            return Response(
                data="can't find is_used flag",
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            serv_settings = request.data['data']
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
            for k, v in setting.items():
                try:
                    service_key_instance = ServiceKey.objects.get(
                        service=service, version=version_query, service_key=k
                    )
                    if service_key_instance.service_value != v:
                        service_key_instance.service_value = v
                        service_key_instance.save()
                        flag = True
                except Exception:
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
