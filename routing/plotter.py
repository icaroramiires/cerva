import os

import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
from shapely.geometry.polygon import Polygon


class Plotter:


	def process_poly(self, poly):

		lat, lon = [], []

		for p in poly:
			lat.append(float(p[0]))
			lon.append(float(p[1]))

		return lat, lon


	def separate_coord_pairs(self, coords):

		lat, lon = [], []

		for coord in coords:

			if type(coord) != list:
				coord = coord.split(',')
			lat.append(float(coord[0]))
			lon.append(float(coord[1]))

		return lat, lon


	def plot_map(self, data, file_name='test', consider=[]):

		#poly = [(41.875668055546626, -87.63382964300646), (41.87564854462585, -87.63382751090967), (41.87562933663752, -87.63382347667482), (41.875610616565076, -87.63381757915384), (41.87559256469304, -87.63380987514307), (41.8755753548708, -87.63380043883633), (41.875559152838356, -87.63378936111044), (41.875544114630145, -87.63377674864994), (41.875530385072324, -87.63376272291971), (41.87551809638805, -87.63374741899521), (41.87550736692406, -87.6337309842616), (41.87549830001097, -87.63371357699435), (41.875490982968095, -87.63369536483495), (41.87548548626257, -87.63367652317648), (41.87548186283066, -87.63365723347437), (41.87548014756801, -87.63363768149901), (41.87548035699353, -87.63361805554662), (41.87548248909034, -87.63359854462584), (41.87548652332517, -87.63357933663752), (41.87549242084616, -87.63356061656506), (41.875500124856934, -87.63354256469303), (41.87550956116366, -87.63352535487078), (41.87552063888956, -87.63350915283834), (41.87553325135006, -87.63349411463014), (41.875547277080294, -87.63348038507232), (41.875562581004786, -87.63346809638804), (41.875579015738396, -87.63345736692406), (41.875596423005646, -87.63344830001097), (41.87561463516504, -87.6334409829681), (41.87563347682353, -87.63343548626256), (41.87565276652564, -87.63343186283066), (41.875672318500996, -87.633430147568), (41.87569194445338, -87.63343035699353), (41.876861944453374, -87.63350035699354), (41.87688145537415, -87.63350248909033), (41.87690066336248, -87.63350652332518), (41.876919383434924, -87.63351242084616), (41.876937435306964, -87.63352012485693), (41.8769546451292, -87.63352956116367), (41.876970847161644, -87.63354063888956), (41.876985885369855, -87.63355325135007), (41.876999614927676, -87.63356727708029), (41.87701190361195, -87.63358258100479), (41.87702263307594, -87.6335990157384), (41.87703169998903, -87.63361642300565), (41.877039017031905, -87.63363463516505), (41.87704451373743, -87.63365347682353), (41.87704813716934, -87.63367276652563), (41.87704985243199, -87.63369231850099), (41.87704964300647, -87.63371194445338), (41.87704751090966, -87.63373145537416), (41.87704347667483, -87.63375066336248), (41.87703757915384, -87.63376938343494), (41.877029875143066, -87.63378743530697), (41.87702043883634, -87.63380464512922), (41.87700936111044, -87.63382084716166), (41.87699674864994, -87.63383588536986), (41.876982722919706, -87.63384961492768), (41.876967418995214, -87.63386190361196), (41.876950984261605, -87.63387263307594), (41.876933576994354, -87.63388169998903), (41.87691536483496, -87.6338890170319), (41.87689652317647, -87.63389451373745), (41.87687723347436, -87.63389813716934), (41.876857681499004, -87.633899852432), (41.87683805554662, -87.63389964300647), (41.875668055546626, -87.63382964300646)]
		#latpoly, lonpoly = self.process_poly(poly)

		plt.clf()
		ax = plt.subplot(111)

		top, left, right, bot = 41.8872, -87.6517, -87.6246, 41.8663

		plt.plot([top, top], [left, right], 'k--')
		plt.plot([top, bot], [left, left], 'k--')
		plt.plot([bot, bot], [left, right], 'k--')
		plt.plot([top, bot], [right, right], 'k--')

		scenario_bounds = Polygon([[top, left], [top, right], [bot, right], [bot, left]])

		for key in data:

			if len(consider) > 0 and str(key) not in consider:
				continue

			coords_list = data[key]

			filtered_coords = []

			for coords in coords_list:

				if type(coords) != list:
					coords = coords.split(',')
				coords = map(float, coords)

				if Point(coords).within(scenario_bounds):

					filtered_coords.append(coords)


			for i in range(1, len(filtered_coords)):

				lat, lon = self.separate_coord_pairs([filtered_coords[i-1], filtered_coords[i]])
				plt.plot(lat, lon, 'c--')

		#plt.plot(latpoly, lonpoly, 'r-', linewidth=1)

		plt.savefig('./routing/mapping/{0}.pdf'.format(file_name), bbox_inches="tight", format='pdf')


	def plot_overlap_map(self, data1, data2, file_name='test'):

		plt.clf()
		ax = plt.subplot(111)

		top, left, right, bot = 41.8872, -87.6517, -87.6246, 41.8663

		plt.plot([top, top], [left, right], 'k--')
		plt.plot([top, bot], [left, left], 'k--')
		plt.plot([bot, bot], [left, right], 'k--')
		plt.plot([top, bot], [right, right], 'k--')

		for key in data1:

			coords_list = data1[key]

			for i in range(1, len(coords_list)):

				lat, lon = self.separate_coord_pairs([coords_list[i-1], coords_list[i]])
				plt.plot(lat, lon, 'r--', alpha=0.5)

		for key in data2:

			coords_list = data2[key]

			for i in range(1, len(coords_list)):

				lat, lon = self.separate_coord_pairs([coords_list[i-1], coords_list[i]])
				plt.plot(lat, lon, 'g--', alpha=0.5)

		plt.savefig('./routing/mapping/{0}.pdf'.format(file_name), bbox_inches="tight", format='pdf')


	def plot_info_traffic(self, road_network, info_flow, mapped, city, folder, file_name='mapped_flow'):

		plt.clf()
		ax = plt.subplot(111)

		top, left, right, bot = 41.8872, -87.6517, -87.6246, 41.8663

		plt.plot([top, top], [left, right], 'k--')
		plt.plot([top, bot], [left, left], 'k--')
		plt.plot([bot, bot], [left, right], 'k--')
		plt.plot([top, bot], [right, right], 'k--')

		scenario_bounds = Polygon([[top, left], [top, right], [bot, right], [bot, left]])

		colors = ['#A2142E', '#C01D2F', '#E85045', '#F6B574', '#FFF4B9', 
				'#D1E890', '#95CF69', '#83CA6E', '#48AD5F', '#238B56', 
				'#147346']

		# Plot net outlier
		for key in road_network:

			coords_list = road_network[key]
			filtered_coords = []

			for coords in coords_list:

				if type(coords) != list:
					coords = coords.split(',')
				coords = map(float, coords)

				if Point(coords).within(scenario_bounds):
					filtered_coords.append(coords)

			color = None
			if key in mapped:
				color = colors[int(float(info_flow[mapped[key]]['JF']))]
			else:
				color = '#147346'

			for i in range(1, len(filtered_coords)):

				lat, lon = self.separate_coord_pairs([filtered_coords[i-1], filtered_coords[i]])
				plt.plot(lat, lon, 'k-', linewidth=1.8)
				plt.plot(lat, lon, '-', color=color, linewidth=1.6, alpha=0.8)

		if not os.path.exists('./routing/mapping/plots'):
			os.makedirs('./routing/mapping/plots')

		if not os.path.exists('./routing/mapping/plots/{0}'.format(city)):
			os.makedirs('./routing/mapping/plots/{0}'.format(city))

		if not os.path.exists('./routing/mapping/plots/{0}/{1}'.format(city, folder)):
			os.makedirs('./routing/mapping/plots/{0}/{1}'.format(city, folder))

		plt.savefig('./routing/mapping/plots/{0}/{1}/{2}.pdf'.format(city, folder, file_name), bbox_inches="tight", format='pdf')