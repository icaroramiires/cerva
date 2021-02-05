import json

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.ticker import PercentFormatter
from shapely.geometry import Point, LineString
from shapely.geometry.polygon import Polygon
from scipy import stats


class Plotter:


	def plot_window_comparison(self, window_scores, window_scores2):

		plt.clf()
		ax = plt.subplot(111)
		plt.plot(range(len(window_scores)), window_scores, 'k-', linewidth=1.8)
		plt.plot(range(len(window_scores)), window_scores2, 'b-', linewidth=1.8)
		plt.show()


	def plot_window(self, window):

		plt.clf()
		ax = plt.subplot(111)
		plt.plot(range(len(window)), window, 'k-', linewidth=1.8)
		plt.show()


	def plot_many_windows(self, file_name='week'):

		plt.savefig('./timewindow/plots/windows_{0}.pdf'.format(file_name.split('.')[0]), bbox_inches="tight", format='pdf')


	def add_one_more(self, window):

		plt.plot(range(len(window)), window, 'k-', linewidth=1.8)


	def initialize_window(self):

		plt.clf()
		ax = plt.subplot(111)


	def plot_all_correlations(self, corr):

		plt.clf()
		ax = plt.subplot(111)

		months = ['Jan.', 'Fev.', 'Mar.', 'Apr.', 'May', 'Jun.', 'Jul.', 'Aug.', 'Set.', 'Oct.', 'Nov.', 'Dec.']

		for i, c in enumerate(corr):
			 plt.plot(range(len(c)), c, label=months[i], linewidth=1.8)

		days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
		plt.xticks(np.arange(0, len(days)), days, rotation=50)
		ax.legend()

		plt.show()


	def read_bounds(self, city):

		f = open('./timewindow/{0}_bounds.json'.format(city), "r")
		bounds = list(f.readlines())
		f.close()

		return bounds


	def format_bounds(self, info):


		info_form = info.replace('[', '').replace(']', '').replace('\n', '')\
						.replace(',', '').strip().split(' ')

		if len(info_form) == 2:
			return (float(info_form[1]), float(info_form[0]))

		return 0, 0


	def get_bounds(self, bounds):

		lats, lons = [], []

		for info in bounds:
			
			lat, lon = self.format_bounds(info)
			if lat != 0:
				lats.append(lat)
				lons.append(lon)
		
		return (lats, lons)


	def calculate_kde(self, data):


		lats, lons = [], []

		print('Iterate')
		for indx, row in data.iterrows():
			lons.append(row['lat'])
			lats.append(row['lon'])

		print('MinMax')
		xmin, xmax = min(lats), max(lats)
		ymin, ymax = min(lons), max(lons)

		X, Y = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]
		positions = np.vstack([X.ravel(), Y.ravel()])
		values = np.vstack([lats, lons])
		
		try:
			print('Gaussian kde')
			kernel = stats.gaussian_kde(values)
			Z = np.reshape(kernel(positions).T, X.shape)

			return Z, xmin, xmax, ymin, ymax
		
		except np.linalg.LinAlgError:
			return


	def plot(self, data, bounds, key):

		plt.clf()
		ax = plt.subplot(111)

		print('Calculate KDE')
		Z, xmin, xmax, ymin, ymax = self.calculate_kde(data)

		print('Imshow')
		ax.imshow(np.rot90(Z), cmap=plt.cm.gist_earth_r,extent=[xmin, xmax, ymin, ymax])
		#ax.imshow(Z, cmap=plt.cm.gist_earth_r, extent=[xmin, xmax, ymin, ymax])

		ax.plot(bounds[1], bounds[0], 'k--', linewidth=1, alpha=0.2)

		print('Save fig')
		#plt.show()
		plt.savefig('./timewindow/plots/{0}.pdf'.format(key.split('.')[0]), bbox_inches="tight", format='pdf')


	def plot_kde(self, data, key):

		city = key.split('_')[2].split('.')[0]

		bounds = self.read_bounds(city)
		print('Get Districts')
		bounds = self.get_bounds(bounds)

		self.plot(data, bounds, key)

		# exit()


	def plot_distribution(self, distribution, month, day):

		plt.clf()
		ax = plt.subplot(111)

		dist_contourn = [d + 0.005 for d in distribution]

		plt.bar(range(0, len(dist_contourn)), dist_contourn, width=1.1, color='#343536')
		N = plt.bar(range(0, len(distribution)), distribution)

		hmax = np.amax(distribution)
		hmin = np.amin(distribution)

		norm = colors.Normalize(hmin, hmax)
		for indx, thispatch in enumerate(N.patches):
			color = plt.cm.Reds(norm(distribution[indx]) + 0.2)
			thispatch.set_facecolor(color)

		plt.xticks(np.arange(0, 577, 48), ['' for i in range(0, 577, 48)])
		# plt.xticks(np.arange(0, 48, 8), np.arange(0, 25, 4))


		# plt.show()
		plt.savefig('./timewindow/plots/distribution/distribution_{0}_{1}.pdf'.format(month, day), bbox_inches="tight", format='pdf')
