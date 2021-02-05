
def calculate_line_diff():
	# SAME LINE
	line1_start = (41.88695, -87.63248)
	line1_end = (41.88692, -87.63539)

	line2_start = (41.88695, -87.62951)
	line2_end = (41.88695, -87.63248)


	# NOT THE SAME LINE
	# line1_start = (41.87523, -87.64807)
	# line1_end = (41.8777, -87.64545)

	# line2_start = (41.87437, -87.64243)
	# line2_end = (41.87432, -87.64711)

	tf_x1 = line1_start[0]
	tf_x2 = line1_end[0]

	tf_y1 = line1_start[1]
	tf_y2 = line1_end[1]


	rn_x1 = line2_start[0]
	rn_x2 = line2_end[0]

	rn_y1 = line2_start[1]
	rn_y2 = line2_end[1]

	tf_m = (tf_x2 - tf_x1) / (tf_y2 - tf_y1)
	rn_m = (rn_x2 - rn_x1) / (rn_y2 - rn_y1)

	if tf_m < 0:
		tf_m = -(tf_m)

	if rn_m < 0:
		rn_m = -(rn_m)

	diff = tf_m - rn_m

	# if diff > 0.05:
	# 	print('DIFF')
	# else:
	# 	print('SAME')


	# print(tf_m)
	# print(rn_m)

############################################################################################################
############################################################################################################
############################################################################################################

from math import atan2, cos, sin, degrees

def verify_angle():

	# lat1 = line1_start[0]
	# lon1 = line1_start[1]
	# lat2 = line1_end[0]
	# lon2 = line1_end[1]

	lat1 = line2_start[0]
	lon1 = line2_start[1]
	lat2 = line2_end[0]
	lon2 = line2_end[1]

	angle = atan2(cos(lat1)*sin(lat2)-sin(lat1) *
	    cos(lat2)*cos(lon2-lon1), sin(lon2-lon1)*cos(lat2))
	bearing = (degrees(angle) + 360) % 360
	print(bearing)

############################################################################################################
############################################################################################################
############################################################################################################


from scipy import stats
import numpy as np
import matplotlib.pyplot as plt

def measure(n):
	"Measurement model, return two coupled measurements."
	m1 = np.random.normal(size=n)
	m2 = np.random.normal(scale=0.5, size=n)
	return m1+m2, m1-m2


def calculate_kde():
	m1, m2 = measure(2000)
	xmin = m1.min()
	xmax = m1.max()
	ymin = m2.min()
	ymax = m2.max()

	print(m1)
	print(m2)

	X, Y = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]
	positions = np.vstack([X.ravel(), Y.ravel()])
	values = np.vstack([m1, m2])
	kernel = stats.gaussian_kde(values)
	Z = np.reshape(kernel(positions).T, X.shape)

	fig, ax = plt.subplots()
	ax.imshow(np.rot90(Z), cmap=plt.cm.gist_earth_r,
			extent=[xmin, xmax, ymin, ymax])
	ax.plot(m1, m2, 'k.', markersize=2)
	ax.set_xlim([xmin, xmax])
	ax.set_ylim([ymin, ymax])
	plt.show()

lats = [41.80057462, 41.803056742, 41.807783124, 41.955842185, 41.925399981, 41.940909163, 41.927006879, 41.758259068, 41.756497643, 41.736613967]
lons = [-87.589225075, -87.603607686, -87.592093307, -87.650268135, -87.658559102, -87.63936916, -87.639020687, -87.615264202, -87.613695282, -87.61444973]

def my_kde():

	xmin, xmax = min(lats), max(lats)
	ymin, ymax = min(lons), max(lons)

	X, Y = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]
	positions = np.vstack([X.ravel(), Y.ravel()])
	values = np.vstack([lats, lons])
	kernel = stats.gaussian_kde(values)
	Z = np.reshape(kernel(positions).T, X.shape)

	print(kernel.pdf([41.87744754022766, -87.64837510877838]))
	print(Z)
	print(np.amax(Z))
	print(np.amin(Z))

	# fig = plt.figure()
	# ax = fig.add_subplot(111)
	# ax.imshow(np.rot90(Z), cmap=plt.cm.gist_earth_r,extent=[xmin, xmax, ymin, ymax])
	# ax.plot(lats, lons, 'k.', markersize=2)
	# ax.set_xlim([xmin, xmax])
	# ax.set_ylim([ymin, ymax])
	# plt.show()

# my_kde()

############################################################################################################
############################################################################################################
############################################################################################################

from sklearn.neighbors import KernelDensity

def calculate():

	x = [[41.80057462, 41.803056742, 41.807783124, 41.955842185, 41.925399981, 41.940909163, 41.927006879, 41.758259068, 41.756497643, 41.736613967],
		[-87.589225075, -87.603607686, -87.592093307, -87.650268135, -87.658559102, -87.63936916, -87.639020687, -87.615264202, -87.613695282, -87.61444973]]
	
	kde = KernelDensity(bandwidth=1.0, kernel='gaussian')
	kde.fit(x[:, None])
	xd = [(41.87744754022766, -87.64837510877838)]
	logprob = kde.score_samples(x_d[:, None])

	print(logprob)

#calculate()


############################################################################################################
############################################################################################################
############################################################################################################

import multiprocessing as mp
import time

def callable_func(param):

	time.sleep(5)
	print(param)
	time.sleep(5)
	print('Leaving {0}'.format(param))


def main_mp():

	processes = []

	for i in range(15):
		processes.append(mp.Process(target=callable_func, args=[i]))

	# Run processes
	for p in processes:
		p.start()

	# Exit the completed processes
	for p in processes:
		p.join()

# main_mp()