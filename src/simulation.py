#!/usr/bin/env python

import subprocess
import os
import logging
import sys
import numpy as np
import json
import multiprocessing as mp

#from optparse import OptionParser
import argparse

import sumo_mannager
import graph_mannager
import traffic_mannager
import traci

#import inspect
#current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#parent_dir = os.path.dirname(current_dir)
#sys.path.insert(0, parent_dir)
from timewindow.contextual import Contextual


class Simulation:


	def iterate_metrics(self, all_metrics):

		traffic, crimes, crashes = [], [], []

		for metrics in all_metrics:
			traffic.append(metrics['traffic'])
			crimes.append(metrics['crimes'])
			crashes.append(metrics['crashes'])

		return traffic, crimes, crashes


	def create_output_file(self, total_count, success_count, error_count, traffic, crimes, crashes, iterate, config, city, day):

		traffic_ms = (np.mean(traffic), np.std(traffic))
		crimes_ms = (np.mean(crimes), np.std(crimes))
		crashes_ms = (np.mean(crashes), np.std(crashes))

		metrics = {}
		metrics['total_count'] = total_count
		metrics['success_count'] = success_count
		metrics['error_count'] = error_count

		metrics['out_traffic'] = map(float, traffic)
		metrics['out_crimes'] = map(float, crimes)
		metrics['out_crashes'] = map(float, crashes)

		metrics['traffic'] = {'mean': float(traffic_ms[0]), 'std': float(traffic_ms[1])}
		metrics['crimes'] = {'mean': float(crimes_ms[0]), 'std': float(crimes_ms[1])}
		metrics['crashes'] = {'mean': float(crashes_ms[0]), 'std': float(crashes_ms[1])}

		with open('./output/data/{0}/{1}/{2}/{3}_metrics.json'.format(day, city, config, iterate), "w") as write_file:
			json.dump(metrics, write_file, indent=4)


	def run(self, network, begin, end, interval, route_log, replication, p, iterate, indx_config, config, city, day):

		logging.debug("Building road graph")
		road_network_graph = graph_mannager.build_road_graph(network)

		error_count, total_count = 0, 0
		logging.debug("Reading contextual data")
		contextual = Contextual(city=city, day=day)

		logging.debug("Running simulation now")
		step = 1
		travel_time_cycle_begin = interval

		road_map = {}
		all_metrics = []

		while step == 1 or traci.simulation.getMinExpectedNumber() > 0:

			logging.debug("Minimum expected number of vehicles: %d" % traci.simulation.getMinExpectedNumber())
			traci.simulationStep()

			if step >= travel_time_cycle_begin and travel_time_cycle_begin <= end and step%interval == 0:

				road_network_graph = traffic_mannager.update_context_on_roads(road_network_graph, contextual, step, indx_config, road_map)
				logging.debug("Updating travel time on roads at simulation time %d" % step)

				error_count, total_count, acumulated_context = traffic_mannager.reroute_vehicles(road_network_graph, p, error_count, total_count, indx_config, road_map)
				all_metrics += acumulated_context

			step += 1

		traffic, crimes, crashes = self.iterate_metrics(all_metrics)

		self.create_output_file(total_count, total_count - error_count, error_count, traffic, crimes, crashes, iterate, config, city, day)

		logging.debug("Simulation finished")
		traci.close()
		sys.stdout.flush()


	def start_simulation(self, sumo, scenario, network, begin, end, interval, output, summary, route_log, replication, p, iterate, indx_config, config, city, day):
		logging.debug("Finding unused port")

		unused_port_lock = sumo_mannager.UnusedPortLock()
		unused_port_lock.__enter__()
		remote_port = sumo_mannager.find_unused_port()

		logging.debug("Port %d was found" % remote_port)

		logging.debug("Starting SUMO as a server")

		sumo = subprocess.Popen([sumo, "-W", "-c", scenario, "--tripinfo-output", output, "--device.emissions.probability", "1.0", "--summary-output", summary,"--remote-port", str(remote_port)], stdout=sys.stdout, stderr=sys.stderr)    
		unused_port_lock.release()

		try:
			traci.init(remote_port)
			self.run(network, begin, end, interval, route_log, replication, float(p), iterate, indx_config, config, city, day)
		except Exception:
			logging.exception("Something bad happened")
		finally:
			logging.exception("Terminating SUMO")
			sumo_mannager.terminate_sumo(sumo)
			unused_port_lock.__exit__()


	def parallel_main_loop(self, city, iterate, config, day, indx_config):

		pred_list = {}

		parser = argparse.ArgumentParser()
		parser.add_argument("-c", "--command", dest="command", default="sumo", help="The command used to run SUMO [default: %default]", metavar="COMMAND")
		parser.add_argument("-s", "--scenario", dest="scenario", default="./scenario/cfgs/{0}/{1}_{2}.sumo.cfg".format(day, city, iterate), help="A SUMO configuration file [default: %default]", metavar="FILE")
		parser.add_argument("-n", "--network", dest="network", default="./scenario/{0}.net.xml".format(city), help="A SUMO network definition file [default: %default]", metavar="FILE")    
		parser.add_argument("-b", "--begin", dest="begin", type=int, default=1500, action="store", help="The simulation time (s) at which the re-routing begins [default: %default]", metavar="BEGIN")
		parser.add_argument("-e", "--end", dest="end", type=int, default=3000, action="store", help="The simulation time (s) at which the re-routing ends [default: %default]", metavar="END")
		parser.add_argument("-i", "--interval", dest="interval", type=int, default=1000, action="store", help="The interval (s) of classification [default: %default]", metavar="INTERVAL")
		parser.add_argument("-o", "--output", dest="output", default="./output/data/{0}/{1}/{2}/{3}_reroute.xml".format(day, city, config, iterate), help="The XML file at which the output must be written [default: %default]", metavar="FILE")
		parser.add_argument("-l", "--logfile", dest="logfile", default="./src/sumo-launchd.log", help="log messages to logfile [default: %default]", metavar="FILE")
		parser.add_argument("-m", "--summary", dest="summary", default="./output/data/{0}/{1}/{2}/{3}_summary.xml".format(day, city, config, iterate), help="The XML file at which the summary output must be written [default: %default]", metavar="FILE")
		parser.add_argument("-r", "--route-log", dest="route_log", default="./output/data/{0}/{1}/{2}/{3}_route-log.txt".format(day, city, config, iterate), help="Log of the entire route of each vehicle [default: %default]", metavar="FILE")
		parser.add_argument("-t", "--replication", dest="replication", default="1", help="number of replications [default: %default]", metavar="REPLICATION")
		parser.add_argument("-p", "--percentage", dest="percentage", default="1", help="percentage of improvement on safety [default: %default]", metavar="REPLICATION")
		
		(options, args) = parser.parse_known_args()

		logging.basicConfig(filename=options.logfile, level=logging.DEBUG)
		logging.debug("Logging to %s" % options.logfile)

		if args:
			logging.warning("Superfluous command line arguments: \"%s\"" % " ".join(args))

		self.start_simulation(options.command, options.scenario, options.network, options.begin, 
			options.end, options.interval, options.output, options.summary, options.route_log, 
			options.replication, options.percentage, iterate, indx_config, config, city, day)

		# if os.path.exists('./src/sumo-launchd.log'):
		# 	os.remove('./src/sumo-launchd.log')


	def main(self, times=20, cities=['austin']):

		print('!# Begin')

		for day in ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']:

			print('! ' + day.capitalize())

			for city in cities:

				print('! City: {0}'.format(city))

				if not os.path.exists('./output/data'):
					os.makedirs('./output/data')

				if not os.path.exists('./output/data/{0}/{1}'.format(day, city)):
					os.makedirs('./output/data/{0}/{1}'.format(day, city))

				for indx_config, config in enumerate(['traffic', 'crimes', 'crashes', 'mtraffic', 'mcrimes', 'mcrashes', 'same', 'traandcri', 'traandcra', 'craandtra', 'craandcri', 'criandtra', 'criandcra', 'none']):

					print('! Config: {0}'.format(config))

					if not os.path.exists('./output/data/{0}/{1}/{2}'.format(day, city, config)):
						os.makedirs('./output/data/{0}/{1}/{2}'.format(day, city, config))

					processes = []

					for ite_cluster in range(0, times // 5):
						processes = [mp.Process(target=self.parallel_main_loop, args=(city, iterate, config, day, indx_config)) for iterate in range(ite_cluster*5, (ite_cluster*5) + 5)]
						# processes = [mp.Process(target=self.parallel_main_loop, args=(city, iterate, config, day, indx_config)) for iterate in range(times)]

						# Run processes
						for p in processes:
							p.start()

						# Exit the completed processes
						for p in processes:
							p.join()

		print('!# End')