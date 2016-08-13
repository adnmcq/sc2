'''
pull data from http://ndb.nal.usda.gov/ndb
my old ndb api key WhLYJ4iMEhodIscJvVy4MCwUC6MBu2QxPd7ZiiDs
my new ndb api key EkuDE4voA1eUHWYINmEoAhAhrSRbNKMtsXQk4Ywf

Make a full list of foods (just a list of the ndbids)
lists of maxrow = 450
there are something like 9500 foods in the database
so you don't need to do that many API hits
to pass into the

'''
import json, urllib2, re, os, csv
from datetime import datetime, timedelta
from threading import Timer
from app.models import *

def run():
	'''
	get all of the foods ids
	then go through list of ids and call the
	'''
	api_key = 'EkuDE4voA1eUHWYINmEoAhAhrSRbNKMtsXQk4Ywf'
	max = 500
	#0-499 offset = 0
	#500 - 999 offset = 500
	#1000 - 1499 offset = 1000
	all_foods = []
	for i in range(3):
		offset = i*max
		#print offset
		total_returned, ids = get_list_of_foods(offset,max,api_key)
		if total_returned == 0:
			break
		else:
			all_foods += ids
	print all_foods
	for food_id in all_foods[:10]:
		try:
			item_data = json.load(urllib2.urlopen('http://api.nal.usda.gov/ndb/reports/?ndbno=%s&type=f&format=json&api_key=%s'%(food_id,api_key)))
			item_data = item_data['report']['food']
			ndbno, name, nutrients = item_data['ndbno'], item_data['name'], item_data['nutrients']
			food, c = Food.objects.get_or_create(name = name, ndbno = ndbno, nut = nutrients)
			print food.name
		except urllib2.HTTPError, e:
			print 'url error', food_id

'''
{
    "report": {
        "sr": "28",
        "type": "Basic",
        "food": {
            "ndbno": "03217",
            "name": "Zwieback",
            "nutrients": [
                {
                    "nutrient_id": "255",
                    "name": "Water",
                    "group": "Proximates",
                    "unit": "g",
                    "value": "4.50",
                    "measures": [
                        {
                            "label": "oz",
                            "eqv": 28.35,
                            "qty": 1.0,
                            "value": "1.28"
                        },
'''


def get_list_of_foods(offset,max,api_key):
	'''
	get a list of foods, 500 at a time
	'''
	list_dict = json.load(urllib2.urlopen('http://api.nal.usda.gov/ndb/list?format=json&max=%s&offset=%s&lt=f&sort=n&api_key=%s'%(max,offset,api_key)))
	total_returned, items = list_dict['list']['total'],list_dict['list']['item']
	ids = []
	for i in items:
		#i = {u'id': u'11009', u'name': u'Artichokes, (globe or french), frozen, unprepared', u'offset': 245}
		ids.append(i['id'])
	return total_returned, ids
