import pandas as pd
import numpy as np
import os, sys
from os import listdir
import json

from scipy.signal import find_peaks, savgol_filter, hilbert, wiener
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
from .plotter import Plotter


class Clustering:


	def encode(self, data):
		data = data.drop(['type', 'hour', 'minute', 'dayofweek'], axis=1)
		return data


	def clusterize(self, data, ep=0.01):

		data_formated = self.encode(data.copy())
		clustering = DBSCAN(eps=ep, min_samples=3).fit_predict(data_formated)
		data['cluster'] = clustering
		
		return data.sort_values('cluster')


class ContextMapping:

	crimes_chicago = ['ASSAULT', 'BATTERY', 'BURGLARY', 'CRIMINAL DAMAGE', 
					 'DECEPTIVE PRACTICE', 'MOTOR VEHICLE THEFT', 'ROBBERY',
					 'THEFT']

	crimes_austin = ['ASSAULT', 'AUTO', 'BURGLARY', 'CRIMINAL', 'FAMILY',
					'POSS', 'THEFT']

	def __init__(self):
		self.MONTHS = {
					1  : 'January',
					2  : 'February',
					3  : 'March',
					4  : 'April',
					5  : 'May',
					6  : 'June',
					7  : 'July',
					8  : 'August',
					9  : 'September',
					10 : 'October',
					11 : 'November',
					12 : 'December',
		}

		self.plotter = Plotter()

	def remove_invalid_coord(self, df):
		return df.query('lat != 0 & lon != 0')


	def read_data(self, folder, file):

		data_file = open(folder + file, 'r')

		context_list = []

		for line in data_file:
			line = line.strip().split('\t')

			item = {}
			item['datetime'] = pd.to_datetime(str(line[0]))
			item['hour'] = pd.to_datetime(str(line[0])).hour
			item['minute'] = pd.to_datetime(str(line[0])).minute
			item['lat'] = float(line[1])
			item['lon'] = float(line[2])
			item['type'] = line[3].strip().split()[0]

			context_list.append(item)

		data_file.close()

		df = pd.DataFrame(context_list)
		df['dayofweek'] = df['datetime'].dt.dayofweek
		df.set_index('datetime', inplace=True)

		return self.remove_invalid_coord(df)


	def read_data_folder(self):

		dfs = {}

		folder = './data/cleaned/'
		for file in listdir(folder):
			print('! File: {0}'.format(file))
			dfs[file] = self.read_data(folder, file)

		return dfs


	def filter_daily(self, df, dayofweek):

		df_filtered = df.query('dayofweek ==' + str(dayofweek))
		return df_filtered


	def make_gauss(self, N=1, sig=1, mu=0):
		return lambda x: N/(sig * (2*np.pi)**.5) * np.e ** (-(x-mu)**2/(105 * sig**2))


	def calculate_difference(self, hour, minute, ref_hour, ref_minute):

		time = hour*60 + minute
		ref_time = ref_hour*60 + ref_minute

		xt = time - ref_time

		score = self.make_gauss()(xt)

		return float('%.5f' % (score))


	def normalize(self, window_scores):

		maxi = np.amax(window_scores)
		mini = np.amin(window_scores)

		for indx, w in enumerate(window_scores):
			window_scores[indx] = (w - mini) / (maxi - mini)

		return window_scores


	def calculate_score(self, crimes_filtered):

		window_scores = []

		for hour in range(0, 24):

			for minute in range(0, 60, 10):

				state_score = []
				for index, row in crimes_filtered.iterrows():
					state_score.append(self.calculate_difference(row['hour'], row['minute'], hour, minute))

				window_scores.append(np.sum(state_score))

		return self.normalize(window_scores)


	def identify_window(self, window_scores, peaks):

		last_peak = 0
		apeaks = []

		peaks.append(len(window_scores)-1)

		for peak in peaks:

			mini = last_peak + np.argmin(window_scores[last_peak:peak])

			if window_scores[mini] == 0.0:
				apeaks.append(mini)

				zero_indx = mini
				while zero_indx < len(window_scores) and window_scores[zero_indx] == 0.0:
					zero_indx += 1
				
				apeaks.append(zero_indx-1)

			else:
				apeaks.append(mini)

			last_peak = peak

		if apeaks[0] < 3:
			apeaks[0] = 0
		if apeaks[0] != 0:
			apeaks.insert(0, 0)

		if apeaks[-1] > len(window_scores) - 3:
			apeaks[-1] = len(window_scores) - 1
		elif apeaks[-1] != len(window_scores)-1:
			apeaks.append(len(window_scores)-1)

		return apeaks


	def get_window(self, start, end, crimes_filtered):

		start_hour = start * 10 // 60
		start_minute = start * 10 % 60

		end_hour = end * 10 // 60
		end_minute = end * 10 % 60

		# Filter the closed interval
		crimes_opened = crimes_filtered.query('hour > {0} & hour < {1}'.format(start_hour, end_hour))

		# Filter the opened interval
		crimes_closed_low = crimes_filtered.query('hour == {0} & minute >= {1}'.format(start_hour, start_minute))
		crimes_closed_high = crimes_filtered.query('hour == {0} & minute < {1}'.format(end_hour, end_minute))

		return pd.concat([crimes_opened, crimes_closed_low, crimes_closed_high])


	def format_data(self, data):

		if data is None:
			return []

		formatted_data = []

		for indx, row in data.iterrows():
			formatted_data.append((row['lat'], row['lon']))

		return formatted_data


	def smooth_scores(self, window_scores):
		return wiener(window_scores)


	def find_window(self, data, clustering, ep=0.01):

		dict_data = {}

		window_scores = self.calculate_score(data)
		window_scores = list(self.smooth_scores(window_scores))

		peaks = find_peaks(window_scores, distance=6)[0].tolist()

		if len(peaks) > 0:
		
			window = self.identify_window(window_scores, peaks)

			if len(window) > 0:

				iterwindow = iter(window)
				next(iterwindow)
				last_window = window[0]
				for iw in iterwindow:

					data_window = self.get_window(last_window, iw, data)

					cluster_data = None
					if len(data_window) >= 3:
						cluster_data = clustering.clusterize(data_window, ep=ep).query('cluster != -1')

					dict_data[str(last_window)] = self.format_data(cluster_data)

					last_window = iw

		return dict_data


	def process(self, month_data, clustering, key):

		windows = {}

		if 'crimes' in key:

			crimes = month_data.groupby('type').all().index

			for crime in crimes:
				if crime in self.crimes_chicago or crime in self.crimes_austin:
					crimes_filtered = month_data.query("type == '%s'" % crime)
					dict_data = self.find_window(crimes_filtered, clustering)
					windows[crime] = dict_data
		else:
			dict_data = self.find_window(month_data, clustering, ep=0.02)
			windows['unkown'] = dict_data

		return windows


	def write_output(self, output_data, day):

		if not os.path.exists('./data/mapped'):
			os.makedirs('./data/mapped')

		with open("./data/mapped/" + str(day) + '.json', "w") as write_file:
			json.dump(output_data, write_file, indent=4)


	def main(self):

		print('!# Begin')

		clustering = Clustering()

		print('! Read all files')
		dfs = self.read_data_folder()

		print('! Process files')

		for indx_day, day in enumerate(['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']):

			print('! Day: {0}'.format(day))
			output_data = {}

			for key in dfs:

				print('! File: {0}'.format(key))

				# key_output = {}

				day_data = self.filter_daily(dfs[key], indx_day)

				# for month in range(1, 13):

				# print('! Month: {0}'.format(self.MONTHS[month]))

				# month_data = day_data['2018-' + str(month)]

				windows = self.process(day_data, clustering, key)

				# key_output[self.MONTHS[month]] = windows

				output_data[key.split('.')[0]] = windows

			self.write_output(output_data, day)

		print('!# End')

