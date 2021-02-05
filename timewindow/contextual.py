import os
import json

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
from shapely.geometry import Point


class Contextual:


	def load_clusters(self, day):
		with open("./data/mapped/" + str(day) + '.json', "r") as file:
			return json.load(file)


	def __init__(self, city='chicago', day='sunday'):
		
		self.city = city
		self.day = day
		
		self.context_data = self.load_clusters(day)

		self.kernels = {}


	def find_last_window(self, windows, step_time):

		windows = list(map(int, windows))
		windows.sort()
		last_window = 0
		for window in windows:
			if window > step_time:
				return str(last_window)

			last_window = window

		return str(last_window)


	def plot_kde(self, kernel, lats, lons, Z, xmin, xmax, ymin, ymax):

		fig = plt.figure()
		ax = fig.add_subplot(111)

		ax.imshow(np.rot90(Z), cmap=plt.cm.gist_earth_r,extent=[xmin, xmax, ymin, ymax])
		ax.plot(lats, lons, 'k.', markersize=2)
		ax.set_xlim([xmin, xmax])
		ax.set_ylim([ymin, ymax])

		plt.show()


	def create_kde(self, contexts, key, last_window):

		# Ref: https://stackoverflow.com/questions/31525393/how-to-plot-kernel-density-estimation-kde-and-zero-crossings-for-3d-data-in-py/31528905#31528905

		if '{0}:{1}'.format(key, last_window) not in self.kernels:

			lats, lons = [], []

			for c in contexts:
				lats.append(c[0])
				lons.append(c[1])

			xmin, xmax = min(lats), max(lats)
			ymin, ymax = min(lons), max(lons)

			X, Y = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]
			positions = np.vstack([X.ravel(), Y.ravel()])
			values = np.vstack([lats, lons])
			
			try:
				kernel = stats.gaussian_kde(values)
				Z = np.reshape(kernel(positions).T, X.shape)
				
				self.kernels['{0}:{1}'.format(key, last_window)] = kernel
				self.kernels['{0}:{1}:min'.format(key, last_window)] = np.amin(Z)
				self.kernels['{0}:{1}:max'.format(key, last_window)] = np.amax(Z)

				#self.plot_kde(kernel ,lats, lons, Z, xmin, xmax, ymin, ymax)

				return True
			
			except np.linalg.LinAlgError:
				return False

		return True


	def calculate_kde(self, contexts, point, key, last_window):
		
		try:
			point_pdf = self.kernels['{0}:{1}'.format(key, last_window)].pdf([point])

			mini, maxi = self.kernels['{0}:{1}:min'.format(key, last_window)], self.kernels['{0}:{1}:max'.format(key, last_window)]

			return float((point_pdf - mini) / (maxi - mini))

		except np.linalg.LinAlgError:
			return 0


	def calculate_score(self, start, end, key, step_time):

		score = [0]

		# Without type
		if self.context_data[key].keys()[0] == 'unknown':
			
			windows = list(self.context_data[key]['unknown'].keys())
			last_window = self.find_last_window(windows, step_time)

			contexts = self.context_data[key]['unknown'][last_window]

			if len(contexts) > 0:
				passed = self.create_kde(contexts, key, last_window)

				if passed:
					score.append(self.calculate_kde(contexts, (start[0], start[1]), key, last_window))
					score.append(self.calculate_kde(contexts, (end[0], end[1]), key, last_window))

		# With type
		else:

			for types in self.context_data[key]:

				windows = list(self.context_data[key][types].keys())
				last_window = self.find_last_window(windows, step_time)

				contexts = self.context_data[key][types][last_window]

				if len(contexts) > 0:
					passed = self.create_kde(contexts, key, last_window)

					if passed:
						score.append(self.calculate_kde(contexts, (start[0], start[1]), key, last_window))
						score.append(self.calculate_kde(contexts, (end[0], end[1]), key, last_window))

		return max(score)


	def prepare_to_return(self, traffic, scores, valid_keys):

		metrics = {}

		metrics['traffic'] = traffic

		for indx, score in enumerate(scores):
			metrics[valid_keys[indx].split('_')[0]] = score

		return metrics


	def trade_off(self, traffic, start, end, step_time, context_weight={'traffic': 1, 'crimes': 1, 'crashes': 1}):

		scores = []
		valid_keys = [str(x) for x in self.context_data if self.city in x]
		valid_keys.sort()
		
		for key in valid_keys:
			scores.append(self.calculate_score(start, end, key, step_time))

		overall_score = traffic*context_weight['traffic']
		if overall_score < 0:
			overall_score = 0
			
		for indx, score in enumerate(scores):
			overall_score += score*context_weight[valid_keys[indx].split('_')[0]]

		if overall_score <= 0:
			overall_score = 0.0001

		return overall_score, self.prepare_to_return(traffic, scores, valid_keys)

