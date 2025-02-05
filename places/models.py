from django.db import models
from django.utils import timezone

class Place(models.Model):
    name = models.CharField(max_length=30)
    type = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    longtitude = models.FloatField()
    latitude = models.FloatField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.ip + ' - ' + str(self.address)
