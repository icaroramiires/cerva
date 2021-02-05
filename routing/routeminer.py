import requests
import json
import os
import random

import gmplot
import matplotlib.pyplot as plt

# 41.87789, -87.65074
# 41.87792, -87.64957
# 41.87793, -87.6484
# 41.87796, -87.64724
# 41.87799, -87.64403
# 41.87802, -87.64258
# 41.87807, -87.64108
# 41.87806, -87.63957


# HERE
APP_ID = ''
APP_CODE = ''

MAPS_KEYS = ['', '']

COORDS_TEST = [[41.87789, -87.65074], [41.87792, -87.64957], [41.87793, -87.6484],
				[41.87796, -87.64724], [41.87799, -87.64403], [41.87802, -87.64258],
				[41.87807, -87.64108], [41.87806, -87.63957]]

class RouteMiner:


	def request_traffic(self, coord):

		global APP_ID, APP_CODE

		url = 'https://isoline.route.api.here.com/routing/7.2/calculateisoline.json'+\
				'?app_id='+APP_ID+\
				'&app_code='+APP_CODE+\
				'&start=geo!'+str(coord[0])+','+str(coord[1])+\
				'&mode=fastest;car;traffic:enabled'+\
				'&range=120'+\
				'&rangetype=time'
				#'&resolution=50'+\

		request = requests.get(url)

		return json.loads(request.text)


	def write_json(self, json_output, output_file):
		
		if not os.path.exists('routing/traffic'):
			os.makedirs('routing/traffic')

		with open('routing/traffic/'+str(output_file)+'.json', 'a') as file:
			json.dump(json_output, file, indent=2)


	def find_traffic_polygons(self, coords):

		polys = []

		for coord in coords:
			polys.append(self.request_traffic(coord))

		self.write_json(polys, 'traffic_polygons')


	def read_json(self, input_file='routing/traffic/traffic_polygons.json'):

		data_file = open(input_file)
		return json.loads(data_file.read())


	def get_coords(self, poly):

		lat, lon = [], []
		for i in poly['response']['isoline'][0]['component'][0]['shape']:
			coords = i.split(',')
			lat.append(float(coords[0]))
			lon.append(float(coords[1]))

		return lat, lon


	def plot_polygons(self, polys):

		gmap = gmplot.GoogleMapPlotter(41.87799, -87.64614, 16)

		#colors = ['#152A55', '#0D4D4B', '#804415', '#7D151A', '#661141', '#401155', '#133253', '#5D0F4C']
		colors = ['firebrick', 'chocolate', 'tan', 'olivedrab', 'seagreen', 'cadetblue', 'royalblue', 'darkmagenta']
		global COORDS_TEST

		for indx, poly in enumerate(polys):
			lat, lon = self.get_coords(poly)
			gmap.polygon(lat, lon, colors[indx], edge_width=2)
			gmap.marker(COORDS_TEST[indx][0], COORDS_TEST[indx][1], colors[indx])

		gmap.draw('routing/traffic/polys.html')


	def main(self):
		
		print('!# Begin')

		#self.find_traffic_polygons(COORDS_TEST)
		polys = self.read_json()
		self.plot_polygons(polys)

		print('!# End')