from __future__ import unicode_literals

from django.db import models
#https://docs.djangoproject.com/en/1.10/ref/contrib/postgres/fields/#django.contrib.postgres.fields.JSONField
from django.contrib.postgres.fields import JSONField

class Food(models.Model):
    name = models.CharField('Name', max_length=200)
    ndbno = models.IntegerField('USDA Nutritional Database Number')
    nut = JSONField()#db_tablespace='table'
    def __str__(self):  # __unicode__ on Python 2
        return self.name