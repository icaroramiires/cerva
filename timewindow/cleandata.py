import numpy as np
import pandas as pd
import os
from os import listdir


FILTERS = {
			'austin_crashes_2018.csv': 
				[],

			'austin_crimes_2018.csv': 
				{'columns': ['Date', 'Type', 'Latitude', 'Longitude'],\
				'types': [str, str, float, float],\
				'positions': [4, 1, 24, 25],\
				'ignore_nan': [0, 0, 0, 0]},

			'chicago_crashes_2018.csv': 
				{'columns': ['Date', 'Type', 'Latitude', 'Longitude'],\
				'types': [str, str, float, float],\
				'positions': [2, 9, 46, 47],\
				'ignore_nan': [0, 0, 0, 0]},

			'chicago_crimes_2018.csv':
				{'columns': ['Date', 'Type', 'Latitude', 'Longitude'],\
				'types': [str, str, float, float],\
				'positions': [1, 4, 14, 15],\
				'ignore_nan': [0, 0, 0, 0]}
}


class CleanData:


	def __init__(self, old_separator=',', new_separator='\t'):
		self.old_separator = old_separator
		self.new_separator = new_separator


	def read_data(self, file, data_header):

		data_file = open(file, 'r')
		data_rows = []
		first_size = 0

		for line in data_file:
			line_clean = line.strip().split(self.old_separator)

			# Ignore columns formated wrongly
			if len(line_clean) != first_size:
				if first_size == 0:
					first_size = len(line_clean) + 1
				continue

			item = {}
			all_ok = True

			for indx, column in enumerate(data_header['columns']):

				try:
					position = data_header['positions'][indx]
					column_type = data_header['types'][indx]
					ignore_nan = data_header['ignore_nan'][indx]

					if not ignore_nan and (line_clean[position].strip() == '' or line_clean[position] == '0'):
						all_ok = False
						break
					item[column] = column_type(line_clean[position])

				except ValueError:
					raise Exception('Invalid data type at column {0}, data {1}, expected type {2}.'.format(column, line[position], column_type))

			if all_ok:
				data_rows.append(item)

		data_file.close()

		data_cleaned = pd.DataFrame(data_rows)

		return data_cleaned


	def read_data_folder(self, folder='./data/input/'):

		dfs = {}

		for file in listdir(folder):
			if file.startswith('.'): continue
			dfs[str(file)] = self.read_data(folder + file, FILTERS[file])

		return dfs


	def write_files(self, files):

		for file in files:
			files[file].to_csv('./data/cleaned/cleaned_' + file, sep=self.new_separator, encoding='utf-8', index=False)


	def main(self):
		
		print('!# Begin')

		print('! Read input files')
		files = self.read_data_folder()

		print('! Write output files')
		self.write_files(files)
		
		print('!# End')

