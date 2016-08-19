from __future__ import unicode_literals

from django.db import models
#https://docs.djangoproject.com/en/1.10/ref/contrib/postgres/fields/#django.contrib.postgres.fields.JSONField
from django.contrib.postgres.fields import JSONField

class Food(models.Model):
    name = models.CharField('Name', max_length=200)
    ndbno = models.IntegerField('USDA Nutritional Database Number')
    nuts = JSONField()
    def __str__(self):  # __unicode__ on Python 2
        return self.name
    def get_units_choices(self):
        '''
        :return: a tuple to be passed into select field
        '''
        nut = self.nuts[0]
        units_choices = [('100 g','100 g')]
        try:
            measures = nut['measures']
            if len(measures)>0:
                for m in measures:
                    json_val = m['label']
                    display = '%s (%s g)'%(m['label'],m['eqv'])
                    units_choices.append((json_val,display))#choices as tuple
            else:
                pass
        except KeyError:
            pass
        return units_choices

class Recipe(models.Model):
    name = models.CharField('Name', max_length=200)
    ingredients = JSONField(null=True)
    nuts = JSONField(null=True)
    def __str__(self):  # __unicode__ on Python 2
        return self.name
