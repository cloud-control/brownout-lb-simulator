#!/usr/bin/env python
from __future__ import division, print_function

## @mainpage
# Documentation for the brownout load-balancer simulator. If confused, start
# with the @ref simulator namespace.

import argparse
import random

from Clients import *
from LoadBalancer import *
from Request import *
from Server import *
from SimulatorKernel import *

## @package simulator Main simulator namespace

## Entry-point for simulator.
# Setups up all entities, then runs simulation.
def main():
	algorithms = ("weighted-RR theta-diff optimization SQF SQF-plus FRF equal-thetas equal-thetas-SQF " + \
		"optim-SQF FRF-EWMA predictive 2RC RR random theta-diff-plus ctl-simplify").split()

	# Parsing command line options to find out the algorithm
	parser = argparse.ArgumentParser( \
		description='Run brownout load balancer simulation.', \
		formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--algorithm',
		help = 'Load-balancer algorithm: ' + ' '.join(algorithms),
		default = algorithms[0])
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
	parser.add_argument('--scenario',
		help = 'Specify a scenario in which to test the system',
		default = os.path.join(os.path.dirname(sys.argv[0]), 'scenarios', 'A.py'))
	args = parser.parse_args()
	algorithm = args.algorithm
	if algorithm not in algorithms:
		print("Unsupported algorithm '{0}'".format(algorithm))
		parser.print_help()
		quit()

	serverControlPeriod = 0.5

	random.seed(1)
	sim = SimulatorKernel(outputDirectory = args.outdir)
	servers = []
	clients = []
	loadBalancer = LoadBalancer(sim, controlPeriod = 1.0)

	loadBalancer.algorithm = algorithm
	loadBalancer.equal_theta_gain = args.equal_theta_gain

	# For weighted-RR algorithm set the weights
	if algorithm == 'weighted-RR':
		servicetimes = np.array([ x.serviceTimeY for x in servers ])
		sumServiceTimes = sum(servicetimes)
		loadBalancer.weights = list(np.array(servicetimes / sumServiceTimes))

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
		server = Server(sim, controlPeriod = serverControlPeriod,
			serviceTimeY = y, serviceTimeN = n, \
			timeSlice = args.timeSlice)
		servers.append(server)
		loadBalancer.addBackend(server)

	def endOfSimulation(at):
		otherParams['simulateUntil'] = at

	# Load scenario
	otherParams = {}
	execfile(args.scenario)
	
	if 'simulateUntil' not in otherParams:
		raise Exception("Scenario does not define end-of-simulation")
	sim.run(until = otherParams['simulateUntil'])

	# Report end results
	recommendationPercentage = float(sim.optionalOn) / float(sim.optionalOff + sim.optionalOn)
	sim.log(sim, loadBalancer.algorithm + \
	    ", total recommendation percentage {0}, standard deviation {1} on mean {2}", \
	    recommendationPercentage, sim.stdServiceTime, sim.avgServiceTime)
	sim.output('final-results', "{algo:15}, {res:.5f}".format(algo = loadBalancer.algorithm, res = recommendationPercentage))

if __name__ == "__main__":
	main()
