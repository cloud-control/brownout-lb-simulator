#!/usr/bin/env python
from __future__ import division, print_function

## @mainpage
# Documentation for the brownout load-balancer simulator. If confused, start
# with the @ref simulator namespace.

import argparse
import os
from os.path import join as pathjoin
import sys
import numpy as np

from BrownoutProxy import *
from Clients import *
from Replica import *
from SimulatorKernel import *

## @package simulator Main simulator namespace

def runSimulation(arrivalRate, outDir, discipline, brownoutMethod, seed):
	with open(pathjoin(outDir, 'parameters.csv'), 'w') as f:
		print('key,value', file = f)
		for k,v in locals().iteritems():
			print(k, v, file = f)

	sim = SimulatorKernel(outputDirectory = outDir)
	replica = Replica(sim = sim,
		seed = seed,
		timeSlice = 0.01 if discipline == 'ps' else 1)

	brownoutProxy = BrownoutProxy(sim = sim, server = replica,
		processorSharing = True if discipline == 'ps' else False,
		queueCut = True if brownoutMethod == 'queuecut' else False)

	client = Client(sim = sim, server = brownoutProxy, rate = arrivalRate, seed = seed)

	sim.run(until = 100)

	# Report results
	return {
		'rtAvg' : avg(client.responseTimes),
		'rtP95' : np.percentile(client.responseTimes, 95),
		'rtP99' : np.percentile(client.responseTimes, 99),
		'rtP999': np.percentile(client.responseTimes, 99.9),
		'rtMax' : max(client.responseTimes),
		'optionalRatio': client.numCompletedRequestsWithOptional / client.numCompletedRequests,
		'utilization'  : replica.getActiveTime() / sim.now,
	}

## Entry-point for simulator.
# Setups up all entities, then runs simulation.
def main():
	# Parsing command line options to find out the algorithm
	parser = argparse.ArgumentParser( \
		description='Run brownout load balancer simulation.', \
		formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--discipline',
		help = 'Service discipline',
		choices = [ 'fifo', 'ps' ],
		default = 'fifo')
	parser.add_argument('--brownoutMethod',
		help = 'Brownout method to deactive optional content',
		choices = [ 'queuecut', 'timecut' ],
		default = 'queuecut')
	parser.add_argument('--seed',
		help = 'Seed to initialize random number generators',
		type = int,
		default = 1)

	args = parser.parse_args()

	header = None
	for arrivalRate in range(1, 10) + range(10, 100, 10):
		outDir = 'results-{0:02d}'.format(arrivalRate)
		try:
			os.makedirs(outDir)
		except:
			pass

		parameters = {
			'arrivalRate'   : arrivalRate,
			'discipline'    : args.discipline,
			'brownoutMethod': args.brownoutMethod,
			'outDir'        : outDir,
			'seed'          : args.seed,
		}
		metrics = runSimulation(**parameters)

		if header is None:
			header = sorted(parameters) + sorted(metrics)
			print(*header, sep = ',')
		metrics.update(parameters)
		print(*[ metrics[k] for k in header ], sep = ',')

if __name__ == "__main__":
	main()
