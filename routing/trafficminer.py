import requests
from here import Here
import time
from datetime import datetime, timedelta


class TrafficMiner:

	SCENARIO = {'chicago': [(41.8872,-87.6517), (41.8663,-87.6246)]}


	def main(self, cities=['austin']):

		global SCENARIO

		print('!# Begin')

		for city in cities:
			print('! ' + city.capitalize())

			print('! Get start info')

			start_info = datetime.now()
			changed_day = False

			while True:

				dt = datetime.now() + timedelta(minutes=10)

				if datetime.now().weekday() != start_info.weekday():
					changed_day = True

				if changed_day and datetime.now().weekday() == start_info.weekday() and datetime.now().hour == start_info.hour:
					break

				print('! Request flow')

				here = Here()
				resp = here.request_flow(SCENARIO[city][0], SCENARIO[city][1])

				file_name = "flow_{0}.xml".format(datetime.now().strftime("%m:%d:%Y_%H:%M"))
				here.save_flow(resp, city, datetime.now().weekday(), file_name)

				print('! Sleeping')
				while True:
					if datetime.now().minute == dt.minute:
						break
					time.sleep(10)


		print('!# End')