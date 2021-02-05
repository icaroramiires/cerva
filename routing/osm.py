import json
import multiprocessing as mp
from math import atan2, cos, sin, degrees
import os

import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
from shapely.geometry.polygon import Polygon


class OSM:


	def read_network(self, city):

		with open("./routing/mapping/{0}_coords.json".format(city), "r") as file:
			return json.load(file)


	def read_id_file(self, file_name='ids_mapped'):

		f = open('./routing/mapping/{0}.txt'.format(file_name), 'r')
		ids_mapped = f.readline().strip()
		ids_sumo = f.readline().strip()
		f.close()

		return ids_mapped, ids_sumo


	def read_mapped(self, city, file_name='ids_mapped'):

		with open("./routing/mapping/{0}_{1}.json".format(city, file_name), "r") as file:
			return json.load(file)


	def calculate_angle(self, line_start, line_end):

		angle = atan2(cos(line_start[0])*sin(line_end[0])-sin(line_start[0]) *
				cos(line_end[0])*cos(line_end[1]-line_start[1]), 
				sin(line_end[1]-line_start[1])*cos(line_end[0]))
		
		bearing = (degrees(angle) + 360) % 360

		return bearing


	def verify_angle(self, tf_line, rn_line):

		tf_angle = self.calculate_angle(list(tf_line.coords)[0], list(tf_line.coords)[1])
		rn_angle = self.calculate_angle(list(rn_line.coords)[0], list(rn_line.coords)[1])

		angle_diff = tf_angle - rn_angle

		if angle_diff < 20 and angle_diff > -20:
			return True
		else:
			if tf_angle > rn_angle:
				if 360 - tf_angle + rn_angle < 20:
					return True
			else:
				if 360 - rn_angle + tf_angle < 20:
					return True

		return False


	def verify_direction(self, tf_line, tf_buffedline, rn_line, rn_buffedline):

		x1 = Point(list(tf_line.coords)[0])
		y1 = Point(list(tf_line.coords)[1])

		x2 = Point(list(rn_line.coords)[0])
		y2 = Point(list(rn_line.coords)[1])

		if tf_line.within(rn_buffedline):

			if x1.distance(x2) < x1.distance(y2) and y1.distance(y2) < y1.distance(x2):
				return True

		elif rn_line.within(tf_buffedline):

			if x2.distance(x1) < x2.distance(y1) and y2.distance(y1) < y2.distance(x1):
				return True

		else:

			if x1.distance(y2) >= x1.distance(x2):
				return True

		return False


	def verify_line_above(self, tf_line, rn_line):

		difference = self.verify_angle(tf_line, rn_line)

		tf_buffedline = tf_line.buffer(0.0002)
		rn_buffedline = rn_line.buffer(0.0002)

		#same_direction = self.verify_direction(tf_line, tf_buffedline, rn_line, rn_buffedline)

		if difference <= 0.05 and tf_buffedline.intersects(rn_buffedline):# and same_direction:
			return True

		return False


	def correlate(self, traffic_flow, road_network, city, file_name='ids_mapped'):
		
		doneit = 0
		wrongit = 0

		mapped = {}

		# Scenario bounds
		top, left, right, bot = 41.8872, -87.6517, -87.6246, 41.8663
		scenario_bounds = Polygon([[top, left], [top, right], [bot, right], [bot, left]])

		for tf in traffic_flow:

			tf_coords = traffic_flow[tf]

			for x in range(1, len(tf_coords)):

				tf_start = map(float, tf_coords[x-1].split(','))
				tf_end = map(float, tf_coords[x].split(','))

				if Point(*tf_start).within(scenario_bounds) and Point(*tf_end).within(scenario_bounds):

					tf_line = LineString([Point(*tf_start), Point(*tf_end)])

					done_line = False

					for rn in road_network:

						rn_coords = road_network[rn]

						for y in range(1, len(rn_coords)):

							rn_start = map(float, rn_coords[y-1])
							rn_end = map(float, rn_coords[y])

							rn_line = LineString([Point(*rn_start), Point(*rn_end)])

							res = self.verify_line_above(tf_line, rn_line)

							if res:
								done_line = True
								mapped[rn] = tf

					if done_line:
						doneit += 1
					else:
						wrongit += 1

		mapped['doneit'] = doneit
		mapped['wrongit'] = wrongit

		with open('./routing/mapping/{0}_{1}.json'.format(city, file_name), 'w') as json_file:
			json.dump(mapped, json_file, indent=4)

		return mapped


	def verify_correlated(self, city, file_name='ids_mapped'):

		if os.path.exists('./routing/mapping/{0}_{1}.json'.format(city, file_name)):
			return True
		return False

