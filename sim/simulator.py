#!/usr/bin/env python
from __future__ import division, print_function

from collections import defaultdict
import heapq
import Queue
import random
import math
import sys

def weightedChoice(choices):
	total = sum(w for c, w in choices)
	r = random.uniform(0, total)
	upto = 0
	for c, w in choices:
		if upto + w > r:
			return c
		upto += w
	assert False, "Shouldn't get here"

class Simulator:
	def __init__(self):
		self.events = []
		self.now = 0.0

	def add(self, delay, what):
		heapq.heappush(self.events, (self.now + delay, what))

	def run(self, until = 1000):
		while self.events:
			self.now, event = heapq.heappop(self.events)
			if self.now > until:
				return
			event()

	def log(self, issuer, message, *args):
		print(self.now, str(issuer), message.format(*args), file = sys.stderr)

class Request:
	lastRequestId = 1
	
	def __init__(self):
		self.requestId = Request.lastRequestId
		Request.lastRequestId += 1

	def __str__(self):
		return str(self.requestId)

class Server:
	lastServerId = 1

	def __init__(self, sim, serviceTimeY = 0.07, serviceTimeN = 0.001, \
			initialTheta = 0.5):
		self.serviceTimeY = serviceTimeY # service time with recommender system
		self.serviceTimeN = serviceTimeN # and without it
		self.controlPeriod = 2 # second
		self.setPoint = 1 # second
		self.pole = 0.9
		self.name = 'server' + str(Server.lastServerId)
		Server.lastServerId += 1

		self.sim = sim
		self.theta = initialTheta
		self.sim.add(0, lambda: self.runControlLoop())
		self.latestLatencies = []
		self.requestQueue = []
		self.activeRequest = None

	def runControlLoop(self):
		if self.latestLatencies:
			serviceTime = max(self.latestLatencies)
			serviceLevel = self.theta

			alpha = serviceTime / serviceLevel # very rough estimate
			# NOTE: control knob allowing to smooth service times
			# To enable this, you *must* add a new state variable (alpha) to the controller.
			#alpha = 0.5 * alpha + 0.5 * serviceTime / previousServiceLevel # very rough estimate
			error = self.setPoint - serviceTime
			# NOTE: control knob allowing slow increase
			if error > 0:
				error *= 0.1
			serviceLevel = serviceLevel + (1 / alpha) * (1 - self.pole) * error

			# saturation, service level is a probability
			serviceLevel = max(serviceLevel, 0.0)
			serviceLevel = min(serviceLevel, 1.0)

			# saturation, it's a probability
			self.theta = min(max(serviceLevel, 0.0), 1.0)
			#self.sim.log(self, "Measured maximum latency {1:.3f}, new theta {0:.2f}", \
			#	self.theta, serviceTime)

			self.latestLatencies = []

		# Re-run later
		self.sim.add(self.controlPeriod, lambda: self.runControlLoop())

	def request(self, request):
		request.arrival = sim.now
		self.requestQueue.append(request)
		self.triggerServer()

	def triggerServer(self):
		# Another request is in progress
		if self.activeRequest:
			return

		# Queue is empty
		if len(self.requestQueue) == 0:
			return

		self.activeRequest = self.requestQueue.pop()
		executeRecommender = random.random() <= self.theta
		self.activeRequest.theta = self.theta
		computationTime = \
			self.serviceTimeY if executeRecommender else self.serviceTimeN
		self.sim.add(computationTime, lambda: self.onCompleted(self.activeRequest))

	def onCompleted(self, request):
		request.completion = self.sim.now
		self.latestLatencies.append(request.completion - request.arrival)
		request.onCompleted()
		self.activeRequest = None
		self.triggerServer()

	def __str__(self):
		return str(self.name)

class LoadBalancer:
	def __init__(self, sim, controlPeriod = 1, initialTheta = 0.5):
		self.controlPeriod = controlPeriod # second
		self.initialTheta = initialTheta

		self.sim = sim
		self.backends = []
		self.weights = []
		self.lastThetas = []
		self.lastLastThetas = []
		
		self.sim.add(0, self.runControlLoop)

	def addBackend(self, backend):
		self.backends.append(backend)
		self.lastThetas.append(self.initialTheta) # to be updated at onComplete
		self.lastLastThetas.append(self.initialTheta) # to be updated at onComplete

		self.weights = [ 1.0 / len(self.backends) ] * len(self.backends)

	def request(self, request):
		#self.sim.log(self, "Got request {0}", request)
		generatedWeight = random.random()
		request.arrival = self.sim.now
		newRequest = Request()
		newRequest.chosenBackendIndex = weightedChoice(zip(range(0, len(self.backends)), self.weights))
		newRequest.originalRequest = request
		newRequest.onCompleted = lambda: self.onCompleted(newRequest)
		#self.sim.log(self, "Directed request to {0}", newRequest.chosenBackendIndex)
		self.backends[newRequest.chosenBackendIndex].request(newRequest)

	def onCompleted(self, request):
		self.lastThetas[request.chosenBackendIndex] = request.theta
		request.completion = self.sim.now
		request.originalRequest.onCompleted()

	def runControlLoop(self):
		self.weights = map(lambda x: max(x[0] + x[1] - x[2], 0.01), \
			zip(self.weights, self.lastThetas, self.lastLastThetas))
		preNormalizedSumOfWeights = sum(self.weights)
		newWeights = map(lambda x: x / preNormalizedSumOfWeights, self.weights)
		self.weights = [0.9 * self.weights[i] + 0.1 * newWeights[i] for i in range(0, len(self.weights))]

		self.sim.add(self.controlPeriod, self.runControlLoop)
		self.sim.log(self, "Measured {1}, New weights {0}", \
			' '.join(["{0:.5f}".format(w) for w in self.weights ]), \
			' '.join(["{0:.5f}".format(t) for t in self.lastThetas ]))
		self.lastLastThetas = self.lastThetas[:]

	def __str__(self):
		return "lb"

class ClosedLoopClient:
	lastClientId = 1

	def __init__(self, sim, server, **kwargs):
		self.averageThinkTime = kwargs.get('thinkTime', 1)
		self.name = 'client' + str(ClosedLoopClient.lastClientId)
		ClosedLoopClient.lastClientId += 1

		self.sim = sim
		self.server = server
		self.sim.add(0, lambda: self.onCompleted(None))

	def issueRequest(self):
		request = Request()
		request.onCompleted = lambda: self.onCompleted(request)
		#self.sim.log(self, "Requested {0}", request)
		self.server.request(request)

	def onCompleted(self, request):
		thinkTime = random.expovariate(1.0 / self.averageThinkTime)
		self.sim.add(thinkTime, self.issueRequest)
		#self.sim.log(self, "Thinking for {0}", thinkTime)
	
	def __str__(self):
		return self.name

if __name__ == "__main__":
	numClients = 50

	sim = Simulator()
	server1 = Server(sim)
	server2 = Server(sim, serviceTimeY = 0.07 * 2, serviceTimeN = 0.001 * 2)
	server3 = Server(sim, serviceTimeY = 0.07 * 3, serviceTimeN = 0.001 * 3)

	lb = LoadBalancer(sim, controlPeriod = 1)
	lb.addBackend(server1)
	lb.addBackend(server2)
	lb.addBackend(server3)

	def addClients(numClients):
		for i in range(0, numClients):
			clients = ClosedLoopClient(sim, lb)

	sim.add(   0, lambda: addClients(numClients))
	sim.add( 500, lambda: addClients(numClients))
	sim.add(1000, lambda: addClients(numClients))
	
	sim.run()
