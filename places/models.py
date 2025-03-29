from django.db import models
from django.utils import timezone

class Dataset(models.Model):
    country = models.CharField(db_index=True, max_length=40)
    country_nr = models.IntegerField()
    url = models.CharField(max_length=254, blank=True, null=True)
    filename = models.CharField(max_length=30, blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now, blank=True)
    count = models.IntegerField(null=True,blank=True)

    def __str__(self):
        return f'{self.country}'



class Place(models.Model):
    name = models.CharField(max_length=30)
    type = models.CharField(db_index=True,max_length=100, blank=True, null=True)
    category = models.CharField(db_index=True,max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(db_index=True,max_length=30)
    longtitude = models.FloatField()
    latitude = models.FloatField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.name}, {self.country}'
