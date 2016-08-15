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
    def get_units(self):
        nut = self.nuts[0]
        units = []
        try:
            measures = nut['measures']
            if len(measures)>0:
                for m in measures:
                    units.append(m['label'])
            else:
                units = ['100 g']
        except KeyError:
            units = ['100 g']
        return units

class Recipe(models.Model):
    name = models.CharField('Name', max_length=200)
    nuts = JSONField()
    def __str__(self):  # __unicode__ on Python 2
        return self.name
    '''
    def get_recipe_items(self):
        #get recipe items for formset initial and nutritional info
        nut = self.nuts[0]
        units = []
        try:
            measures = nut['measures']
            if len(measures)>0:
                for m in measures:
                    units.append(m['label'])
            else:
                units = ['100 g']
        except KeyError:
            units = ['100 g']
        return units
    '''


'''
nutrients = Food.objects.get(whatever).nuts

nutrient = filter(lambda n: n.get('name') == 'Manganese, Mn', nutrients)'

nutrient_value = nutrient.get('value')
nutrient_unit =
'''