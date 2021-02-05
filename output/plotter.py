import os
import json
import math

import numpy as np
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup


class Plotter:


	METRIC_UNIT = {'duration' : 'seconds',
					'route_length': 'meters',
					'time_loss': 'seconds',
					'traffic' : 'traffic load score',
					'crimes': 'insecurity level',
					'crashes': 'accident probability'}


	def read_xml_file(self, file):

		f = open(file)
		data = f.read()
		soup = BeautifulSoup(data, "xml")
		f.close()

		return soup


	def read_json_file(self, file):

		with open(file, "r") as file:
			return json.load(file)


	def mean_confidence_interval(self, data, confidence=0.95):
		a = 1.0 * np.array(data)
		n = len(a)
		m, se = np.mean(a), np.std(a)
		h = 1.96 * (se/math.sqrt(n))
		return (m, h)


	def get_reroute_metrics(self, ires):

		duration, route_length, time_loss = [], [], []

		tripinfos = ires.find('tripinfos')

		for info in tripinfos.findAll('tripinfo'):

			try:
				dur = float(info['duration'])
				rou = float(info['routeLength'])
				tim = float(info['timeLoss'])

				if dur > 10.00 and rou > 50.00:
					duration.append(dur)
					route_length.append(rou)
					time_loss.append(tim)
			except Exception:
				pass

		return np.mean(duration), np.mean(route_length), np.mean(time_loss)


	def calculate_reroute_metrics(self, accumulated):

		return {'duration': self.mean_confidence_interval(accumulated['duration']),
				'route_length': self.mean_confidence_interval(accumulated['route_length']),
				'time_loss': self.mean_confidence_interval(accumulated['time_loss'])}


	def read_reroute_files(self, results, days, cities):

		for city in cities:

			for folder in os.listdir('./output/data/monday/{0}'.format(city)):

				accumulated = {'duration': [],
							'route_length': [],
							'time_loss': []}

				for day in days:

					for iterate in range(20):
						ires = self.read_xml_file('./output/data/{0}/{1}/{2}/{3}_reroute.xml'.format(day, city, folder, iterate))
						dur, rou, tim = self.get_reroute_metrics(ires)
						accumulated['duration'].append(dur)
						accumulated['route_length'].append(rou)
						accumulated['time_loss'].append(tim)

				results['reroute_{0}_{1}'.format(city, folder)] = self.calculate_reroute_metrics(accumulated)

		return results


	def get_contextual_metrics(self, ires):
		return float(ires['traffic']['mean']), float(ires['crimes']['mean']), float(ires['crashes']['mean'])


	def calculate_contextual_metrics(self, accumulated):

		return {'traffic': self.mean_confidence_interval(accumulated['traffic']),
				'crimes': self.mean_confidence_interval(accumulated['crimes']),
				'crashes': self.mean_confidence_interval(accumulated['crashes'])}


	def read_contextual_files(self, results, days, cities):

		for city in cities:

			for folder in os.listdir('./output/data/monday/{0}'.format(city)):

				accumulated = {'traffic': [],
							'crimes': [],
							'crashes': []}

				for day in days:

					for iterate in range(20):
						ires = self.read_json_file('./output/data/{0}/{1}/{2}/{3}_metrics.json'.format(day, city, folder, iterate))
						tra, cri, cra = self.get_contextual_metrics(ires)
						accumulated['traffic'].append(tra)
						accumulated['crimes'].append(cri)
						accumulated['crashes'].append(cra)

				results['context_{0}_{1}'.format(city, folder)] = self.calculate_contextual_metrics(accumulated)

		return results


	def save_calculation(self, results, file='all'):

		if not os.path.exists('results'):
			os.makedirs('results')

		with open('results/{0}_results.json'.format(file), "w") as write_file:
			json.dump(results, write_file, indent=4)


	def read_calculation(self):

		results = {}

		for file in os.listdir('results/'):

			with open('results/{0}'.format(file), "r") as write_file:
				results[file] = json.load(write_file)

		return results


	def filter_keys(self, results, sfilter='context'):

		filtered_keys = [x for x in results.keys() if sfilter in x]

		filtered_dict = {}
		for f in filtered_keys:
			filtered_dict[f] = results[f]

		metrics = results[filtered_keys[0]].keys()

		return filtered_dict, metrics


	def separate_mean_std(self, just_to_plot, metric, keys_order, cities):

		means, stds = [], []

		for city in cities:
			for key in keys_order:
				k = [x for x in just_to_plot if key in x and city in x][0]

				means.append(just_to_plot[k][metric][0])
				stds.append(just_to_plot[k][metric][1])

		return means, stds


	def plot_dots(self, just_to_plot, metric, file, cities):

		if not os.path.exists('metric_plots'):
		    os.makedirs('metric_plots')

		plt.clf()
		ax = plt.subplot(111)

		keys_order = ['traffic', 'crimes', 'crashes', 'mtraffic', 'mcrimes', 'mcrashes', 'same', 'traandcri', 'traandcra', 'craandtra', 'craandcri', 'criandtra', 'criandcra', 'none']

		xlabels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'None']

		means, stds = self.separate_mean_std(just_to_plot, metric, keys_order, cities)

		colorlist = ['#1d4484', '#7c0404', '#86a4ca', '#5dddd0', '#874a97', '#e6f0fc', '#424564']

		for indx, city in enumerate(cities):
			plt.errorbar([x for x in range(14)], means[indx*14:(indx+1)*14], yerr=stds[indx*14:(indx+1)*14], fmt='o-.', color=colorlist[indx], label=city.capitalize(), capsize=5)

		plt.xlabel('Execution Configuration')
		plt.ylabel('{0} ({1})'.format(metric.replace('_', ' ').capitalize(), self.METRIC_UNIT[metric]))
		plt.xticks(np.arange(0, len(xlabels)), xlabels, rotation=50)

		ax.legend()

		plt.savefig('metric_plots/{0}_{1}.pdf'.format(file, metric), bbox_inches="tight", format='pdf')


	def plot(self, results, file, cities):

		contextual, cmetrics = self.filter_keys(results)
		mobility, mmetrics = self.filter_keys(results, sfilter='reroute')

		for metric in cmetrics:
			self.plot_dots(contextual, metric, file, cities)

		for metric in mmetrics:
			self.plot_dots(mobility, metric, file, cities)


	def main(self, cities=['austin']):

		results = {}
		days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']

		# print('Read reroute files')
		# self.read_reroute_files(results, days, cities)

		# print('Read contextual files')
		# self.read_contextual_files(results, days, cities)

		# print('Save calculations')
		# self.save_calculation(results)

		# for day in days:

		# 	print(day)

		# 	results = {}
		# 	print('Read reroute files')
		# 	self.read_reroute_files(results, [day], cities)

		# 	print('Read contextual files')
		# 	self.read_contextual_files(results, [day], cities)

		# 	print('Save calculations')
		# 	self.save_calculation(results, day)

		print('Read calculation')
		results = self.read_calculation()

		print('Plot')
		for res in results:
			self.plot(results[res], res, cities)
