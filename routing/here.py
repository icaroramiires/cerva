import requests
import json
import os
from bs4 import BeautifulSoup
from collections import OrderedDict


DAYS = {'0': 'monday',
		'1': 'tuesday',
		'2': 'wednesday',
		'3': 'thursday',
		'4': 'friday',
		'5': 'saturday',
		'6': 'sunday'}


class Here:


	def __init__(self, APP_ID="", APP_CODE=""):

		self.APP_ID = APP_ID
		self.APP_CODE = APP_CODE


	def request_isoline(self, coords):

		url = 'https://isoline.route.api.here.com/routing/7.2/calculateisoline.json'

		params = {
			'app_id': self.APP_ID,
			'app_code': self.APP_CODE,
			'start': 'geo!' + str(coords[0]) + ',' + str(coords[1]),
			'mode': 'fastest;car;traffic:enabled',
			'range': 120,
			'rangetype': 'time'
		}

		response = requests.get(url, params)

		return json.loads(response.text)


	def request_flow(self, coords_topleft=(41.8872,-87.6517), coords_bottomright=(41.8663,-87.6246)):

		url = 'https://traffic.api.here.com/traffic/6.2/flow.xml'

		params = {
			'app_id': self.APP_ID,
			'app_code': self.APP_CODE,
			'bbox': '{0},{1};{2},{3}'.format(coords_topleft[0], coords_topleft[1], coords_bottomright[0], coords_bottomright[1]),
			'responseattributes': 'sh'
		}

		response = requests.get(url, params)

		return BeautifulSoup(response.text, "xml")


	def save_flow(self, data, city, day, file_name='test.xml'):

		global DAYS

		if not os.path.exists('./routing/flows'):
			os.makedirs('./routing/flows')

		if not os.path.exists('./routing/flows/{0}'.format(city)):
			os.makedirs('./routing/flows/{0}'.format(city))

		if not os.path.exists('./routing/flows/{0}/{1}'.format(city, DAYS[str(day)])):
			os.makedirs('./routing/flows/{0}/{1}'.format(city, DAYS[str(day)]))

		f = open('routing/flows/{0}/{1}/{2}'.format(city, DAYS[str(day)], file_name), 'w')
		f.write(data.prettify())
		f.close()


	def read_flow(self, city, file_name='scenario.xml'):

		f = open('routing/flows/{0}/{1}'.format(city, file_name), 'r')
		data = f.read()
		soup = BeautifulSoup(data, "xml")
		f.close()

		return soup


	def get_pbt(self, data):

		return data.find('TRAFFICML_REALTIME').find('RWS').find('RW')['PBT']


	def format_flow(self, data):

		formatted = {}
		info = {}

		fi_tags = data.findAll('FI')

		for fi in fi_tags:

			pc = fi.find('TMC')['PC']
			ff = fi.find('CF')['FF']
			jf = fi.find('CF')['JF']
			sp = fi.find('CF')['SP']

			shps_coord = []
			
			for shp in fi.findAll('SHP'):
			
				coords = shp.text.strip().split(' ')
				shps_coord.extend(coords)

			# Remove all the duplicates
			shps_coord = list(OrderedDict.fromkeys(shps_coord))
			
			formatted[pc] = shps_coord
			info[pc] = {'FF': ff, 'JF': jf, 'SP': sp}

		return formatted, info


