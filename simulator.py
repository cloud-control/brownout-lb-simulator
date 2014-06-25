#!/usr/bin/env python
from __future__ import division, print_function

## @mainpage
# Documentation for the brownout load-balancer simulator. If confused, start
# with the @ref simulator namespace.

import argparse
import os
import sys

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
	parser.add_argument('--outdir',
		help = 'Destination folder for results and logs',
		default = '.')
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

	sim = SimulatorKernel(outputDirectory = args.outdir)
	replica = Replica(sim = sim, timeSlice = args.timeSlice)
	client = Client(sim = sim, server = replica, rate = 10)

	sim.run(until = 100)

if __name__ == "__main__":
	main()
