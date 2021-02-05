import os

from here import Here
from osm import OSM
from plotter import Plotter


class FlowManager:


	def main(self, cities=['austin']):

		print('!# Begin')

		for city in cities:
			print('! ' + city.capitalize())

			print('! Read flow')
			here = Here()
			traffic_flow = here.read_flow(city)

			print('! Format flow')
			formatted_flow, info_flow = here.format_flow(traffic_flow)

			print('! Read network')
			osm = OSM()
			road_network = osm.read_network(city)

			if not osm.verify_correlated(city):
				print('! Correlate')
				osm.correlate(formatted_flow, road_network, city)

			print('! Read ids')
			#ids_mapped, ids_sumo = osm.read_id_file()
			mapped = osm.read_mapped(city)

			plotter = Plotter()

			for folder in os.listdir('./routing/flows/{0}'.format(city)):

				if not 'scenario' in folder:

					for file in os.listdir('./routing/flows/{0}/{1}'.format(city, folder)):

						print('! Read here files')

						print('! File: {0}'.format(file))
						traffic_flow = here.read_flow(city, file_name='{0}/{1}'.format(folder, file))
						formatted_flow, info_flow = here.format_flow(traffic_flow)

						print('! Plot map')
						# plotter.plot_map(formatted_flow, file_name='flow')
						# plotter.plot_map(road_network, file_name='network')
						# plotter.plot_overlap_map(formatted_flow, road_network, file_name='overlap')
						# plotter.plot_map(formatted_flow, file_name='consider_flow', consider=ids_mapped)
						# plotter.plot_map(road_network, file_name='consider_network', consider=ids_sumo)
						plotter.plot_info_traffic(road_network, info_flow, mapped, city, folder, file_name=file.split('.')[0])

		print('!# End')