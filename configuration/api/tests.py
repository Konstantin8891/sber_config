import os

# from django.core.files import File
from django.test import Client, TestCase
from django.urls import reverse

from http import HTTPStatus

import configuration.settings as settings

from configs.models import Service, ServiceKey, ServiceVersion


class Test(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = Service.objects.create(name='test1')
        cls.service_version = ServiceVersion.objects.create(
            service=cls.service,
            version='test1',
            is_used=False
        )
        cls.service_used_version = ServiceVersion.objects.create(
            service=cls.service,
            version='test2',
            is_used=True
        )

        cls.service_key = ServiceKey.objects.create(
            service=cls.service,
            version=cls.service_version,
            service_key='test',
            service_value='test'
        )
        cls.service_key_used = ServiceKey.objects.create(
            service=cls.service,
            version=cls.service_used_version,
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


    def test_delete_unused_record(self):
        self.guest_client.delete('/config?service=test1&version=test1')
        self.assertFalse(ServiceKey.objects.filter(
            service=self.service,
            version=self.service_version,
            service_key='test',
            service_value='test'
        ).exists())

    def test_delete_used_record(self):
        self.guest_client.delete('/config?service=test1&version=test2')
        self.assertTrue(ServiceKey.objects.filter(
            service=self.service,
            version=self.service_used_version,
            service_key='test',
            service_value='test'
        ).exists())

