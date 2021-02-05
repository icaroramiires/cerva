import sys
import argparse
import warnings

from timewindow.cleandata import CleanData
from timewindow.contextmapping import ContextMapping
from scenario.generator import Generator
from routing.routeminer import RouteMiner
from routing.trafficminer import TrafficMiner
from routing.flowmanager import FlowManager
from src.simulation import Simulation
from output.plotter import Plotter


'''
	Tasks:
	--cd: CleanData
	Clean tabular data according to it's columns and generate output

	--cm: ContextMapping
	Identifies timewindow, apply clustering, and save clusters at 'mapped/' folder

	--ge: Generator
	Generate the execution cfgs and trips

	--ro: RouteMiner
	Mine routes and converts to simulator

	--tm: TrafficMiner
	Mine traffic and saves the result

	--fm: FlowManager
	Maps the flow to the .net edge ids

	--si: Simulation
	Simulate the available scenarios

	--pl: Plotter
	Plot the generated results
'''
TASKS = {
		'cd' : CleanData(),
		'cm' : ContextMapping(),
		'ge' : Generator(),
		'ro' : RouteMiner(),
		'tm' : TrafficMiner(),
		'fm' : FlowManager(),
		'si' : Simulation(),
		'pl' : Plotter()
}


class Ring:

	def main(self, args):
		global TASKS
		print('!##### Initiated with args: {0}'.format(args))

		if args.cd: 
			print('!### Task: cd')
			call = TASKS['cd']
			call.main()

		if args.cm: 
			print('!### Task: cm')
			call = TASKS['cm']
			call.main()

		if args.ge: 
			print('!### Task: ge')
			call = TASKS['ge']
			call.main(times=args.times[0], cities=args.cities)

		if args.ro:
			print('!### Task: ro')
			call = TASKS['ro']
			call.main()

		if args.tm:
			print('!### Task tm')
			call = TASKS['tm']
			call.main(cities=args.cities)

		if args.fm:
			print('### Task fm')
			call = TASKS['fm']
			call.main(cities=args.cities)

		if args.si: 
			print('!### Task: si')
			call = TASKS['si']
			call.main(times=args.times[0], cities=args.cities)

		if args.pl: 
			print('!### Task: pl')
			call = TASKS['pl']
			call.main(cities=args.cities)

if __name__ == '__main__':

	warnings.simplefilter("ignore")

	parser = argparse.ArgumentParser(description='Context-aware and Personalized ITS.')
	parser.add_argument('--times', metavar='t', type=int, nargs=1, default=20, action='store', help='Quantity of times executed')
	parser.add_argument('--cities', metavar='c', type=str, nargs='*', default=['austin'], action='store', help='Lower case city name')
	parser.add_argument('--cd', help='Clean data', action='store_true')
	parser.add_argument('--cm', help='Context mapping', action='store_true')
	parser.add_argument('--ge', help='Scenario generator', action='store_true')
	parser.add_argument('--ro', help='Route miner', action='store_true')
	parser.add_argument('--tm', help='Traffic miner', action='store_true')
	parser.add_argument('--fm', help='Flow manager', action='store_true')
	parser.add_argument('--si', help='Simulation', action='store_true')
	parser.add_argument('--pl', help='Plotter', action='store_true')

	args = parser.parse_args()

	ruler = Ring()
	ruler.main(args)

