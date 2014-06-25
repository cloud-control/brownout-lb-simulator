#!/usr/bin/env python
from __future__ import division, print_function

## @mainpage
# Documentation for the brownout load-balancer simulator. If confused, start
# with the @ref simulator namespace.

import argparse
import os
import sys
import numpy as np

from BrownoutProxy import *
from Clients import *
from Replica import *
from SimulatorKernel import *

## @package simulator Main simulator namespace

## Entry-point for simulator.
# Setups up all entities, then runs simulation.
def main():
	# Parsing command line options to find out the algorithm
	parser = argparse.ArgumentParser( \
		description='Run brownout load balancer simulation.', \
		formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--timeSlice',
		type = float,
		help = 'Time-slice of server scheduler',
		default = 0.01)

	group = parser.add_argument_group('rc', 'General replica controller options')
	group.add_argument('--rcSetpoint',
		type = float,
		help = 'Replica controller setpoint',
		default = 1)
	group.add_argument('--rcPercentile',
		type = float,
		help = 'What percentile reponse time to drive to target',
		default = 95)

	args = parser.parse_args()

	print("arrivalRate,rtAvg,rt95,rt99,rtMax,optionalRatio")

	for arrivalRate in range(1, 30):
		outDir = 'results-{0:02d}'.format(arrivalRate)
		try:
			os.makedirs(outDir)
		except:
			pass

		sim = SimulatorKernel(outputDirectory = outDir)
		replica = Replica(sim = sim, timeSlice = args.timeSlice)
		brownoutProxy = BrownoutProxy(sim = sim, server = replica)
		client = Client(sim = sim, server = brownoutProxy, rate = arrivalRate)

		sim.run(until = 100)

		# Report results
		rtAvg = avg(client.responseTimes)
		rtP95 = np.percentile(client.responseTimes, 95)
		rtP99 = np.percentile(client.responseTimes, 99)
		rtMax = max(client.responseTimes)
		optionalRatio = client.numCompletedRequestsWithOptional / client.numCompletedRequests
		print(arrivalRate, rtAvg, rtP95, rtP99, rtMax, optionalRatio, sep = ',')

if __name__ == "__main__":
	main()
