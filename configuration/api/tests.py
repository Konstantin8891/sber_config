from pyexpat import version_info
from wsgiref.simple_server import server_version
from django.test import Client, TestCase
from django.urls import reverse

from http import HTTPStatus

from configs.models import Service, ServiceKey, ServiceVersion


class Test(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = Service.objects.create(name='test1')
        cls.service_version = ServiceVersion.objects.create(
            service=cls.service,
            version='test1'
        )
        cls.service_key = ServiceKey.objects.create(
            service=cls.service,
            version=cls.service_version,
            service_key='test',
            service_value='test'
        )
        cls.service_key_count = ServiceKey.objects.count()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
    
    def test_get_endpoint(self):
        response = self.guest_client.get('/config?service=test1&version=test1')
        self.assertEqual(response.status_code, HTTPStatus.OK)
    
    def test_post_endpoint_new_version_existing_service(self):
        self.guest_client.post(
            reverse('config'),
            data={
                "service": "test1",
                "version": "test2",
                "data": [
                    {"key1": "value1"},
                ]
            },
            content_type='application/json'
        )
        self.assertEqual(ServiceKey.objects.count(), self.service_key_count + 1)
        version = ServiceVersion.objects.get(service=self.service, version='test2')
        self.assertTrue(ServiceKey.objects.filter(
            service=self.service,
            version=version,
            service_key='key1',
            service_value='value1'
        ).exists())

    def test_post_endpoint_new_service(self):
        self.guest_client.post(
            reverse('config'),
            data={
                "service": "test2",
                "version": "test1",
                "data": [
                    {"key1": "value1"},
                ]
            },
            content_type='application/json'
        )        
        self.assertEqual(ServiceKey.objects.count(), self.service_key_count + 1)
        service = Service.objects.get(name='test2')
        version = ServiceVersion.objects.get(service=service, version='test1')
        self.assertTrue(ServiceKey.objects.filter(
            service=service,
            version=version,
            service_key='key1',
            service_value='value1'
        ).exists())

    def test_patch_endpoint(self):
        self.guest_client.patch(
            reverse('config'),
            data={
                "service": "test1",
                "version": "test1",
                "data": [
                    {"key1": "value1"},
                ]
            },
            content_type='application/json'
        )
        self.assertTrue(ServiceKey.objects.filter(
            service=self.service,
            version=self.service_version,
            service_key='key1',
            service_value='value1'
        ).exists())

    def test_delete_record(self):
        self.guest_client.post(
            reverse('config'),
            data={
                "service": "test2",
                "version": "test1",
                "data": [
                    {"key1": "value1"},
                ]
            },
            content_type='application/json'
        )
        self.guest_client.delete('/config?service=test1&version=test1')
        service = Service.objects.get(name='test2')
        version = ServiceVersion(service=service, version='test1')
        self.assertFalse(ServiceKey.objects.filter(
            service=service,
            version=version,
            service_key='key1',
            service_value='value1'
        ).exists())

    def test_put_endpoint_existing_record(self):
        self.guest_client.put(
            reverse('config'),
            data={
                "service": "test1",
                "version": "test1",
                "data": [
                    {"key1": "value1"},
                ]
            },
            content_type='application/json'
        )
        self.assertTrue(ServiceKey.objects.filter(
            service=self.service,
            version=self.service_version,
            service_key='key1',
            service_value='value1'
        ).exists())

    def test_put_endpoint_new_record(self):
        self.guest_client.put(
            reverse('config'),
            data={
                "service": "test2",
                "version": "test1",
                "data": [
                    {"key1": "value1"},
                ]
            },
            content_type='application/json'
        )
        service = Service.objects.get(name='test2')
        version = ServiceVersion.objects.get(service=service, version='test1')
        self.assertEqual(ServiceKey.objects.count(), self.service_key_count + 1)
        self.assertTrue(ServiceKey.objects.filter(
            service=service,
            version=version,
            service_key='key1',
            service_value='value1'
        ).exists())
