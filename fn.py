'''
Pull data from http://ndb.nal.usda.gov/ndb
my old ndb api key WhLYJ4iMEhodIscJvVy4MCwUC6MBu2QxPd7ZiiDs
my new ndb api key EkuDE4voA1eUHWYINmEoAhAhrSRbNKMtsXQk4Ywf


'''
import json, urllib2, re, os, csv
from datetime import datetime, timedelta
from threading import Timer
from app.models import *

def run():
	'''
	Pull nutritional data from http://ndb.nal.usda.gov/ndb
	my old ndb api key WhLYJ4iMEhodIscJvVy4MCwUC6MBu2QxPd7ZiiDs
	my new ndb api key EkuDE4voA1eUHWYINmEoAhAhrSRbNKMtsXQk4Ywf


	You can only make 1000 API things per hour
	Get list of nbdids to look up nutrients

	API Query for certain foods
	Get nutrient info for 950 foods every hour

	There are something like 9500 foods in the database

	So run over the course of 10-12 hours
	'''
	api_key = 'EkuDE4voA1eUHWYINmEoAhAhrSRbNKMtsXQk4Ywf'
	max = 500
	#0-499 offset = 0
	#500 - 999 offset = 500
	#1000 - 1499 offset = 1000
	all_foods = []
	for i in range(30):
		offset = i*max
		total_returned, ids = get_list_of_foods(offset, max, api_key)
		if total_returned == 0:
			break
		else:
			all_foods += ids
	print all_foods
	for i in range(12):
		start = i*950
		finish = start+950
		#Timer(seconds, function, [parameters]).start()
		food_list = all_foods[start:finish]
		Timer(i*3600+i*10, get_segment, [api_key, food_list]).start()


def get_list_of_foods(offset, max, api_key):
	'''
	Get a list of foods, 500 at a time
	'''
	list_dict = json.load(urllib2.urlopen('http://api.nal.usda.gov/ndb/list?format=json&max=%s&offset=%s&lt=f&sort=n&api_key=%s'%(max,offset,api_key)))
	total_returned, items = list_dict['list']['total'],list_dict['list']['item']
	ids = []
	for i in items:
		#i = {u'id': u'11009', u'name': u'Artichokes, (globe or french), frozen, unprepared', u'offset': 245}
		ids.append(i['id'])
	return total_returned, ids


def get_segment(api_key, food_list):
	'''
	Get nutrient info for foods - 900 at a time
	'''
	for food_id in food_list:
		try:
			item_data = json.load(urllib2.urlopen('http://api.nal.usda.gov/ndb/reports/?ndbno=%s&type=f&format=json&api_key=%s'%(food_id, api_key)))
			item_data = item_data['report']['food']
			ndbno, name, nutrients = item_data['ndbno'], item_data['name'], item_data['nutrients']
			food, c = Food.objects.get_or_create(name = name, ndbno = ndbno, nuts = nutrients)
			food.name = replace_unicrap(food.name)
			print food.name
		except urllib2.HTTPError, e:
			print 'url error', food_id


def replace_unicrap(unicrap_string):
	"""This replaces UNICODE Latin-1 characters with
	something equivalent in 7-bit ASCII. All characters in the standard
	7-bit ASCII range are preserved. In the 8th bit range all the Latin-1
	accented letters are stripped of their accents. Most symbol characters
	are converted to something meaningful. Anything not converted is deleted.
	MOAR HERE --- http://unicodelookup.com/#latin/3
	"""
	xlate = {
		0xc0: 'A', 0xc1: 'A', 0xc2: 'A', 0xc3: 'A', 0xc4: 'A', 0xc5: 'A',
		0xc6: 'Ae', 0xc7: 'C',
		0xc8: 'E', 0xc9: 'E', 0xca: 'E', 0xcb: 'E',
		0xcc: 'I', 0xcd: 'I', 0xce: 'I', 0xcf: 'I',
		0xd0: 'Th', 0xd1: 'N',
		0xd2: 'O', 0xd3: 'O', 0xd4: 'O', 0xd5: 'O', 0xd6: 'O', 0xd8: 'O',
		0xd9: 'U', 0xda: 'U', 0xdb: 'U', 0xdc: 'U',
		0xdd: 'Y', 0xde: 'th', 0xdf: 'ss',
		0xe0: 'a', 0xe1: 'a', 0xe2: 'a', 0xe3: 'a', 0xe4: 'a', 0xe5: 'a',
		0xe6: 'ae', 0xe7: 'c',
		0xe8: 'e', 0xe9: 'e', 0xea: 'e', 0xeb: 'e',
		0xec: 'i', 0xed: 'i', 0xee: 'i', 0xef: 'i',
		0xf0: 'th', 0xf1: 'n',
		0xf2: 'o', 0xf3: 'o', 0xf4: 'o', 0xf5: 'o', 0xf6: 'o', 0xf8: 'o',
		0xf9: 'u', 0xfa: 'u', 0xfb: 'u', 0xfc: 'u',
		0xfd: 'y', 0xfe: 'th', 0xff: 'y', 0x161 :'s',0xF6:'o',
		0xa1: '!', 0xa2: '{cent}', 0xa3: '{pound}', 0xa4: '{currency}',
		0xa5: '{yen}', 0xa6: '|', 0xa7: '{section}', 0xa8: '{umlaut}',
		0xa9: '{C}', 0xaa: '{^a}', 0xab: '<<', 0xac: '{not}',
		0xad: '-', 0xae: '{R}', 0xaf: '_', 0xb0: '{degrees}',
		0xb1: '{+/-}', 0xb2: '{^2}', 0xb3: '{^3}', 0xb4:"'",
		0xb5: '{micro}', 0xb6: '{paragraph}', 0xb7: '*', 0xb8: '{cedilla}',
		0xb9: '{^1}', 0xba: '{^o}', 0xbb: '>>',
		0xbc: '{1/4}', 0xbd: '{1/2}', 0xbe: '{3/4}', 0xbf: '?',
		0xd7: '*', 0xf7: '/',0x2026:'...',0xA9:'(c)'
	}
	r = ''
	for i in unicrap_string:
		if xlate.has_key(ord(i)):
			r += xlate[ord(i)]
		elif ord(i) >= 0x80:
			pass
		else:
			r += i
	return r

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



