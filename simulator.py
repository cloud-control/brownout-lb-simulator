#!/usr/bin/env python
from __future__ import division, print_function

## @mainpage
# Documentation for the brownout load-balancer simulator. If confused, start
# with the @ref simulator namespace.

import argparse
import os
from os.path import join as pathjoin
import numpy as np

from BrownoutProxy import BrownoutProxy
from Clients import Client
from Replica import Replica
from SimulatorKernel import SimulatorKernel

from utils import avg

## @package simulator Main simulator namespace

def runSimulation(params):
	with open(pathjoin(params['outDir'], 'parameters.csv'), 'w') as _file:
		print('name,value', file=_file)
		for name, value in params.iteritems():
			print(name, value, sep=',', file=_file)

	sim = SimulatorKernel(outputDirectory=params['outDir'])
	replica = Replica(sim=sim,
		seed=params['seed'],
		timeSlice=(0.01 if params['discipline'] == 'ps' else 1),
		timeY=(params['timeYmu'], params['timeYsigma']),
		timeN=(params['timeNmu'], params['timeNsigma']))

	brownoutProxy = BrownoutProxy(sim=sim, server=replica,
		processorSharing=(True if params['discipline'] == 'ps' else False),
		queueCut=(True if params['brownoutMethod'] == 'queuecut' else False))

	client = Client(sim=sim, server=brownoutProxy, rate=params['arrivalRate'],
		seed=params['seed'])

	sim.run(until=100)

	# Report results
	# pylint: disable=no-member
	return {
		'rtAvg' : avg(client.responseTimes),
		'rtP95' : np.percentile(client.responseTimes, 95),
		'rtP99' : np.percentile(client.responseTimes, 99),
		'rtP999': np.percentile(client.responseTimes, 99.9),
		'rtMax' : max(client.responseTimes),
		'optionalRatio': client.numCompletedWithOptional / client.numCompleted,
		'utilization'  : replica.getActiveTime() / sim.now,
	}
	# pylint: enable=no-member

## Entry-point for simulator.
# Setups up all entities, then runs simulation.
def main():
	# Parsing command line options to find out the algorithm
	parser = argparse.ArgumentParser( \
		description='Run brownout load balancer simulation.', \
		formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--discipline',
		help='Service discipline',
		choices=['fifo', 'ps'],
		default='fifo')
	parser.add_argument('--brownoutMethod',
		help='Brownout method to deactive optional content',
		choices=['queuecut', 'timecut'],
		default='queuecut')
	parser.add_argument('--seed',
		help='Seed to initialize random number generators',
		type=int,
		default=1)

	args = parser.parse_args()

	header = None
	for relativeDeviation in range(1, 50):
		for seed in range(1, 4):
			for arrivalRate in range(1, 10) + range(10, 100, 10):
				parameters = {
					'arrivalRate'   : arrivalRate,
					'discipline'    : args.discipline,
					'brownoutMethod': args.brownoutMethod,
					'seed'          : seed,
					'relativeDeviation': relativeDeviation,
					'timeYmu'       : 0.07,
					'timeYsigma'    : 0.07 * relativeDeviation / 100,
					'timeNmu'       : 0.00067,
					'timeNsigma'    : 0.00067 * relativeDeviation / 100,
				}

				outDir = '-'.join(
					['results'] +
					[v for v in parameters.itervalues() if type(v) == str] +
					['{0}{1:04d}'.format(k, v)
						for k, v in parameters.iteritems() if type(v) == int]
				)
				try:
					os.makedirs(outDir)
				except OSError:
					pass
				parameters['outDir'] = outDir
				metrics = runSimulation(parameters)

				# pylint: disable=star-args
				if header is None:
					header = sorted(parameters) + sorted(metrics)
					print(*header, sep=',')
				metrics.update(parameters)
				print(*[metrics[k] for k in header], sep=',')
				# pylint: enable=star-args

if __name__ == "__main__":
	main()
