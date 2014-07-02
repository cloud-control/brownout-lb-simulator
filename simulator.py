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
	parser.add_argument('--processorSharing',
		help = 'Use processor sharing service discipline (default: %default)',
		default = False)
	parser.add_argument('--queueCut',
		help = 'Cut based on queue-length, not processing time (default: %default)',
		default = False)

	args = parser.parse_args()

	print("#", ' '.join(sys.argv))
	print("arrivalRate,rtAvg,rt95,rt99,rt999,rtMax,optionalRatio,utilization")

	for arrivalRate in range(1, 50):
		outDir = 'results-{0:02d}'.format(arrivalRate)
		try:
			os.makedirs(outDir)
		except:
			pass

		sim = SimulatorKernel(outputDirectory = outDir)
		replica = Replica(sim = sim,
			timeSlice = 0.01 if args.processorSharing else 1)

		brownoutProxy = BrownoutProxy(sim = sim, server = replica,
			processorSharing = args.processorSharing,
			queueCut = args.queueCut)

		client = Client(sim = sim, server = brownoutProxy, rate = arrivalRate)

		sim.run(until = 100)

		# Report results
		rtAvg = avg(client.responseTimes)
		rtP95 = np.percentile(client.responseTimes, 95)
		rtP99 = np.percentile(client.responseTimes, 99)
		rtP999 = np.percentile(client.responseTimes, 99.9)
		rtMax = max(client.responseTimes)
		optionalRatio = client.numCompletedRequestsWithOptional / client.numCompletedRequests
		utilization = replica.getActiveTime() / sim.now
		print(arrivalRate, rtAvg, rtP95, rtP99, rtP999, rtMax, optionalRatio, utilization, sep = ',')

if __name__ == "__main__":
	main()
