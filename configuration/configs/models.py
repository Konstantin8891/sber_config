from django.db import models


class Service(models.Model):
    name = models.TextField()


class ServiceVersion(models.Model):
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE
    )
    version = models.TextField()


class ServiceKey(models.Model):
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
    )
    version = models.ForeignKey(
        ServiceVersion,
        on_delete=models.CASCADE
    )
    service_key = models.TextField()
    service_value = models.TextField()
