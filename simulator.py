#!/usr/bin/env python
from __future__ import division, print_function

## @mainpage
# Documentation for the brownout load-balancer simulator. If confused, start
# with the @ref simulator namespace.

import argparse
import numpy as np
import os
import sys

from plants import AutoScaler, ClosedLoopClient, OpenLoopClient, LoadBalancer, Server
from base import Request, SimulatorKernel
from base.utils import *
from controllers import loadControllerFactories

loadBalancingAlgorithms = ("weighted-RR theta-diff SQF SQF-plus FRF equal-thetas equal-thetas-SQF " + \
		"FRF-EWMA predictive 2RC RR random theta-diff-plus ctl-simplify equal-thetas-fast theta-diff-plus-SQF " + \
		"theta-diff-plus-fast SRTF equal-thetas-fast-mul").split()

## @package simulator Main simulator namespace

## Entry-point for simulator.
# Setups up all entities, then runs simulation(s).
def main():
	# Load all controller factories
	autoScalerControllerFactories = loadControllerFactories('autoscaler')
	replicaControllerFactories = loadControllerFactories('server')

	# Parsing command line options to find out the algorithm
	parser = argparse.ArgumentParser( \
		description='Run brownout load balancer simulation.', \
		formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--algorithm',
		help = 'Load-balancer algorithm: ' + ' '.join(loadBalancingAlgorithms),
		default = loadBalancingAlgorithms[0])
	parser.add_argument('--outdir',
		help = 'Destination folder for results and logs',
		default = 'results')
	parser.add_argument('--timeSlice',
		type = float,
		help = 'Time-slice of server scheduler',
		default = 0.01)
	parser.add_argument('--equal-theta-gain',
		type = float,
		help = 'Gain in the equal-theta algorithm',
		default = 0.025) #0.117)
	parser.add_argument('--equal-thetas-fast-gain',
		type = float,
		help = 'Gain in the equal-thetas-fast algorithm',
		default = 2.0) #0.117)
	parser.add_argument('--scenario',
		help = 'Specify a scenario in which to test the system',
		default = os.path.join(os.path.dirname(sys.argv[0]), 'scenarios', 'replica-steady-1.py'))

	group = parser.add_argument_group('ac', 'General autoscaler controller options')
	group.add_argument('--ac',
		help = 'Autoscaler controller: ' + ' '.join([ acf.getName() for acf in autoScalerControllerFactories ]),
		default = 'trivial')

	# Add autoscaler controller factories specific command-line arguments
	for acf in autoScalerControllerFactories:
		group = parser.add_argument_group("Options for '{0}' autoscaler controller".format(acf.getName()))
		acf.addCommandLine(group)

	group = parser.add_argument_group('rc', 'General replica controller options')
	group.add_argument('--rc',
		help = 'Replica controller: ' + ' '.join([ rcf.getName() for rcf in replicaControllerFactories ]),
		default = 'static')
	group.add_argument('--rcSetpoint',
		type = float,
		help = 'Replica controller setpoint',
		default = 1)
	group.add_argument('--rcPercentile',
		type = float,
		help = 'What percentile reponse time to drive to target',
		default = 95)

	# Add replica controller factories specific command-line arguments
	for rcf in replicaControllerFactories:
		group = parser.add_argument_group("Options for '{0}' replica controller".format(rcf.getName()))
		rcf.addCommandLine(group)

	args = parser.parse_args()
	algorithm = args.algorithm
	if algorithm not in loadBalancingAlgorithms:
		print("Unsupported algorithm '{0}'".format(algorithm), file = sys.stderr)
		parser.print_help()
		quit()

	# Find autoscaler controller factory
	try:
		autoScalerControllerFactory = filter(lambda ac: ac.getName() == args.ac, autoScalerControllerFactories)[0]
	except IndexError:
		print("Unsupported autoscaler controller '{0}'".format(args.ac), file = sys.stderr)
		parser.print_help()
		quit()

	# Find replica controller factory
	try:
		replicaControllerFactory = filter(lambda rc: rc.getName() == args.rc, replicaControllerFactories)[0]
	except IndexError:
		print("Unsupported replica controller '{0}'".format(args.rc), file = sys.stderr)
		parser.print_help()
		quit()

	# Allow controller factories to analyse command-line
	autoScalerControllerFactory.parseCommandLine(args)
	replicaControllerFactory.parseCommandLine(args)

	runSingleSimulation(
			outdir = args.outdir,
			autoScalerControllerFactory = autoScalerControllerFactory,
			replicaControllerFactory = replicaControllerFactory,
			scenario = args.scenario,
			timeSlice = args.timeSlice,
			algorithm = args.algorithm,
			equal_theta_gain = args.equal_theta_gain,
			equal_thetas_fast_gain = args.equal_thetas_fast_gain
	)

## Runs a single simulation
# @param outdir folder in which results should be written
# @param autoScalerControllerFactory factory for the auto-scaler controller
# @param replicaControllerFactory factory for the replica controller
# @param scenario file containing the scenario
# @param timeSlice time-slice for the server processor-sharing model
# @param algorithm load-balancing algorithm name (TODO: move to loadBalancerControllerFactory)
# @param equal_theta_gain parameter for load-balancing algorithm (TODO: move to loadBalancerControllerFactory)
# @param equal_thetas_fast_gain paramater for load-balancing algorithm (TODO: move to loadBalancerControllerFactory)
def runSingleSimulation(outdir, autoScalerControllerFactory, replicaControllerFactory, scenario, timeSlice,
		algorithm, equal_theta_gain, equal_thetas_fast_gain):
	sim = SimulatorKernel(outputDirectory = outdir)
	servers = []
	clients = []
	loadBalancer = LoadBalancer(sim, controlPeriod = 1.0)
	autoScaler = AutoScaler(sim, loadBalancer,
				controller = autoScalerControllerFactory.newInstance(sim, 'as-ctr'))
	openLoopClient = OpenLoopClient(sim, autoScaler)

	loadBalancer.algorithm = algorithm
	loadBalancer.equal_theta_gain = equal_theta_gain
	loadBalancer.equal_thetas_fast_gain = equal_thetas_fast_gain

	# Define verbs for scenarios
	def addClients(at, n):
		def addClientsHandler():
			for _ in range(0, n):
				clients.append(ClosedLoopClient(sim, loadBalancer))
		sim.add(at, addClientsHandler)

	def delClients(at, n):
		def delClientsHandler():
			for _ in range(0, n):
				client = clients.pop()
				client.deactivate()
		sim.add(at, delClientsHandler)

	def changeServiceTime(at, serverId, y, n):
		def changeServiceTimeHandler():
			server = servers[serverId]
			server.serviceTimeY = y
			server.serviceTimeN = n
		sim.add(at, changeServiceTimeHandler)
		
	def addServer(y, n, autoScale = False):
		server = Server(sim, \
			serviceTimeY = y, serviceTimeN = n, \
			timeSlice = timeSlice)
		newReplicaController = replicaControllerFactory.newInstance(sim, str(server) + "-ctl")
		server.controller = newReplicaController
		servers.append(server)
		if autoScale:
			autoScaler.addBackend(server)
		else:
			loadBalancer.addBackend(server)
	
	def setRate(at, rate):
		sim.add(at, lambda: openLoopClient.setRate(rate))
	
	def endOfSimulation(at):
		otherParams['simulateUntil'] = at
		
	# Load scenario
	otherParams = {}
	execfile(scenario)

	# For weighted-RR algorithm set the weights
	if algorithm == 'weighted-RR':
		serviceRates = np.array([ 1.0/x.serviceTimeY for x in servers ])
		sumServiceRates = sum(serviceRates)
		loadBalancer.weights = list(np.array(serviceRates / sumServiceRates))
	
	if 'simulateUntil' not in otherParams:
		raise Exception("Scenario does not define end-of-simulation")
	sim.run(until = otherParams['simulateUntil'])

	# Report end results
	responseTimes = reduce(lambda x,y: x+y, [client.responseTimes for client in clients], []) + openLoopClient.responseTimes
	numRequestsWithOptional = sum([client.numCompletedRequestsWithOptional for client in clients]) + openLoopClient.numCompletedRequestsWithOptional

	toReport = []
	toReport.append(( "loadBalancingAlgorithm", algorithm.ljust(20) ))
	toReport.append(( "replicaAlgorithm", replicaControllerFactory.getName().ljust(20) ))
	toReport.append(( "numRequests", str(len(responseTimes)).rjust(7) ))
	toReport.append(( "numRequestsWithOptional", str(numRequestsWithOptional).rjust(7) ))
	toReport.append(( "optionalRatio", "{:.3f}".format(numRequestsWithOptional / len(responseTimes)) ))
	toReport.append(( "avgResponseTime", "{:.3f}".format(avg(responseTimes)) ))
	toReport.append(( "p95ResponseTime", "{:.3f}".format(np.percentile(responseTimes, 95)) ))
	toReport.append(( "p99ResponseTime", "{:.3f}".format(np.percentile(responseTimes, 99)) ))
	toReport.append(( "maxResponseTime", "{:.3f}".format(max(responseTimes)) ))
	toReport.append(( "stddevResponseTime", "{:.3f}".format(np.std(responseTimes)) ))

	print(*[k for k,v in toReport], sep = ', ')
	print(*[v for k,v in toReport], sep = ', ')

	sim.output('final-results', ', '.join([k for k,v in toReport]))
	sim.output('final-results', ', '.join([v for k,v in toReport]))

if __name__ == "__main__":
	main() # pragma: no cover
