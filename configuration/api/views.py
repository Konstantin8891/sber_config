from urllib import response
from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import KeySerializer
from configs.models import Service, ServiceKey, ServiceVersion


@api_view(['GET', 'POST', 'PATCH', 'DELETE', 'PUT'])
def hello(request):
    if request.method == 'POST':
        name = request.data['service']
        serv_settings = request.data['data']
        flag = False
        for find_ver in serv_settings:
            try:
                version = find_ver['version']
                flag = True
            except:
                pass
        if not flag:
            return Response(data='no version in file', status=status.HTTP_400_BAD_REQUEST)
        try:
            service = Service.objects.get(name=name)
            if ServiceVersion.objects.filter(service=service, version=version).exists():
                return Response(data='config already exists', status=status.HTTP_400_BAD_REQUEST)
            ver_created = ServiceVersion.objects.create(service=service, version=version)
            for setting in serv_settings:
                for k, v in setting.items():
                    ServiceKey.objects.create(service=service, version=ver_created, service_key=k, service_value=v)
            return Response(data='created', status=status.HTTP_201_CREATED)
        except:
            service = Service.objects.create(name=name)
            ver_created = ServiceVersion.objects.create(service=service, version=version)
            for setting in serv_settings:
                for k, v in setting.items():
                    ServiceKey.objects.create(service=service, version=ver_created, service_key=k, service_value=v)
            return Response(data='created', status=status.HTTP_201_CREATED)
    if request.method == 'PATCH':
        name = request.data['service']
        serv_settings = request.data['data']
        flag = False
        for find_ver in serv_settings:
            try:
                version = find_ver['version']
                flag = True
            except:
                pass
        if not flag:
            return Response(data='no version in file', status=status.HTTP_400_BAD_REQUEST)
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
                version_query = ServiceVersion.objects.get(service=service, version=version)
            except:
                version_query = ServiceVersion.objects.create(service=service, version=version)
            for setting in serv_settings:
                for k, v in setting.items():
                    try:
                        service_key_instance = ServiceKey.objects.get(service=service, version=version_query, service_key=k)
                        if service_key_instance.service_value != v:
                            service_key_instance.service_value = v
                            service_key_instance.save()
                            flag = True
                    except:
                        ServiceKey.objects.create(service=service, version=version_query, service_key=k, service_value=v)
                        flag = True
            if flag:
                return Response(data='changed', status=status.HTTP_206_PARTIAL_CONTENT)
            return Response(data='no changes', status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(data='record does not exist', status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        # name = request.data['service']
        name = request.query_params.get('service')
        try:
            service = Service.objects.get(name=name)
            service.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(data='no record', status=status.HTTP_400_BAD_REQUEST)
    name = request.query_params.get('service')
    if request.method == 'PUT':
        name = request.data['service']
        serv_settings = request.data['data']
        service, _ = Service.objects.get_or_create(name=name)
        for find_ver in serv_settings:
            try:
                version = find_ver['version']
                flag = True
            except:
                pass
        if not flag:
            return Response(data='no version in file', status=status.HTTP_400_BAD_REQUEST)
        version_query, _ = ServiceVersion.objects.get_or_create(service=service, version=version)
        flag = False
        for setting in serv_settings:
            for k, v in setting.items():
                try:
                    service_key_instance = ServiceKey.objects.get(service=service, version=version_query, service_key=k)
                    if service_key_instance.service_value != v:
                        service_key_instance.service_value = v
                        service_key_instance.save()
                        flag = True
                except:
                    ServiceKey.objects.create(service=service, version=version_query, service_key=k, service_value=v)
                    flag = True
        
                # ServiceKey.objects.update_or_create(service=service, version=version_query, service_key=k, service_value=v)
        if flag:
            return Response(data='put', status=status.HTTP_201_CREATED)
        return Response(data='no changes', status=status.HTTP_400_BAD_REQUEST)
    try:
        service = Service.objects.get(name=name)
        service_key_instance = ServiceKey.objects.filter(service=service)
        data = {}
        for s_k in service_key_instance:
            serializer = KeySerializer(instance=s_k)
            data = data | serializer.data
        return Response(data=data, status=status.HTTP_200_OK)
    except:
        Response(data='record not found', status=status.HTTP_400_BAD_REQUEST)
