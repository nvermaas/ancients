from django.db import models
from django.utils import timezone

class Place(models.Model):
    name = models.CharField(max_length=30)
    type = models.CharField(db_index=True,max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(db_index=True,max_length=30)
    longtitude = models.FloatField()
    latitude = models.FloatField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.name}, {self.country}'
