#!/usr/bin/env python
from __future__ import division, print_function

## @mainpage
# Documentation for the brownout load-balancer simulator. If confused, start
# with the @ref simulator namespace.

import argparse
import os
import sys

from Clients import *
from LoadBalancer import *
from Request import *
from Server import *
from SimulatorKernel import *

## @package simulator Main simulator namespace

## Entry-point for simulator.
# Setups up all entities, then runs simulation.
def main():
	# Load all replica controllers
	replicaControllers = []
	# XXX: TODO

	algorithms = ("weighted-RR theta-diff optimization SQF SQF-plus FRF equal-thetas equal-thetas-SQF " + \
		"optim-SQF FRF-EWMA predictive 2RC RR random theta-diff-plus ctl-simplify equal-thetas-fast theta-diff-plus-SQF " + \
		"theta-diff-plus-fast SRTF equal-thetas-fast-mul oracle").split()

	# Parsing command line options to find out the algorithm
	parser = argparse.ArgumentParser( \
		description='Run brownout load balancer simulation.', \
		formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--algorithm',
		help = 'Load-balancer algorithm: ' + ' '.join(algorithms),
		default = algorithms[0])
	parser.add_argument('--replicaController',
		help = 'Replica controller',
		default = '')
	parser.add_argument('--replicaSetPoint',
		type = float,
		help = 'Replica controller setpoint',
		default = 1)
	parser.add_argument('--replicaSetPointType',
		help = 'Replica controller setpoint type: avg, 95, 99, max',
		default = '95')
	parser.add_argument('--outdir',
		help = 'Destination folder for results and logs',
		default = '.')
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
	args = parser.parse_args()
	algorithm = args.algorithm
	if algorithm not in algorithms:
		print("Unsupported algorithm '{0}'".format(algorithm))
		parser.print_help()
		quit()

	serverControlPeriod = 0.5

	sim = SimulatorKernel(outputDirectory = args.outdir)
	servers = []
	clients = []
	loadBalancer = LoadBalancer(sim, controlPeriod = 1.0)
	openLoopClient = OpenLoopClient(sim, loadBalancer)

	loadBalancer.algorithm = algorithm
	loadBalancer.equal_theta_gain = args.equal_theta_gain
	loadBalancer.equal_thetas_fast_gain = args.equal_thetas_fast_gain

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
		
	def addServer(y, n):
		server = Server(sim, \
			serviceTimeY = y, serviceTimeN = n, \
			timeSlice = args.timeSlice)
		servers.append(server)
		loadBalancer.addBackend(server)
	
	def setRate(at, rate):
		sim.add(at, lambda: openLoopClient.setRate(rate))
	
	def setQueueOffset(server, queueOffset):
		loadBalancer.queueOffsets[server] = queueOffset

	def endOfSimulation(at):
		otherParams['simulateUntil'] = at

	def setQueueOffset(server, queueOffset):
		loadBalancer.queueOffsets[server] = queueOffset
		
	# Load scenario
	otherParams = {}
	execfile(args.scenario)

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
	toReport.append(( "replicaAlgorithm", "periodic".ljust(20) ))
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
	main()
