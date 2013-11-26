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
		self.now = 0

	def add(self, delay, what):
		heapq.heappush(self.events, (self.now + delay, what))

	def run(self, until = 100):
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

	def __init__(self, sim, **kwargs):
		self.serviceTimeY = 0.02 # service time with recommender system
		self.serviceTimeN = 0.001 # and without it
		self.controlPeriod = 1 # second
		self.setPoint = 1 # second
		self.name = 'server' + str(Server.lastServerId)
		Server.lastServerId += 1

		self.sim = sim
		self.theta = kwargs.get('initialTheta', 0.5)
		self.sim.add(0, lambda: self.runControlLoop())
		self.latestLatencies = []
		self.requestQueue = []

	def runControlLoop(self):
		if self.latestLatencies:
			c_est = max(self.latestLatencies) / self.theta # very rough estimate
			pole = 0.9
			error = self.setPoint - max(self.latestLatencies)
			self.theta += (1/c_est) * (1 - pole) * error

			# saturation, it's a probability
			self.theta = min(max(self.theta, 0.0), 1.0)

			self.latestLatencies = []

		# Re-run later
		self.sim.add(self.controlPeriod, lambda: self.runControlLoop())

	def request(self, request):
		request.arrival = sim.now
		if self.requestQueue:
			self.requestQueue.push(request)
		else:
			self.serve(request)

	def serve(self, request):
		executeRecommender = random.random() <= self.theta
		request.theta = self.theta
		computationTime = \
			self.serviceTimeY if executeRecommender else self.serviceTimeN
		self.sim.add(computationTime, lambda: self.onCompleted(request))

	def onCompleted(self, request):
		request.completion = self.sim.now
		self.latestLatencies.append(request.completion - request.arrival)
		request.onCompleted()
		if self.requestQueue:
			request = self.requestQueue.pop()
			self.sim.add(0, lambda: self.serve(request))

class LoadBalancer:
	def __init__(self, sim, **kwargs):
		self.controlPeriod = 1 # second
		self.initialTheta = kwargs.get('initialTheta', 0.5)

		self.sim = sim
		self.backends = []
		self.weights = []
		self.lastThetas = []
		
		self.sim.add(0, self.runControlLoop)

	def addBackend(self, backend):
		self.backends.append(backend)
		self.lastThetas.append(self.initialTheta) # to be updated at onComplete

		self.weights = [ 1.0 / len(self.backends) ] * len(self.backends)

	def request(self, request):
		self.sim.log(self, "Got request {0}", request)
		generatedWeight = random.random()
		request.arrival = self.sim.now
		newRequest = Request()
		newRequest.chosenBackendIndex = weightedChoice(zip(range(0, len(self.backends)), self.weights))
		newRequest.originalRequest = request
		newRequest.onCompleted = lambda: self.onCompleted(newRequest)
		self.sim.log(self, "Directed request to {0}", newRequest.chosenBackendIndex)
		self.backends[newRequest.chosenBackendIndex].request(newRequest)

	def onCompleted(self, request):
		self.lastThetas[request.chosenBackendIndex]
		request.completion = self.sim.now
		request.originalRequest.onCompleted()

	def runControlLoop(self):
		sumOfThetas = sum(self.lastThetas)
		self.weights = map(lambda x: x / sumOfThetas, self.lastThetas)
		self.sim.add(self.controlPeriod, self.runControlLoop)

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
		self.sim.add(0, self.issueRequest)

	def issueRequest(self):
		request = Request()
		request.onCompleted = lambda: self.onCompleted(request)
		self.sim.log(self, "Requested {0}", request)
		self.server.request(request)

	def onCompleted(self, request):
		thinkTime = random.expovariate(1.0 / self.averageThinkTime)
		self.sim.add(thinkTime, self.issueRequest)
		self.sim.log(self, "Thinking for {0}", thinkTime)
	
	def __str__(self):
		return self.name

if __name__ == "__main__":
	numClients = 1

	sim = Simulator()
	server1 = Server(sim)
	server2 = Server(sim)

	lb = LoadBalancer(sim)
	lb.addBackend(server1)
	lb.addBackend(server2)

	clients = []
	for i in range(0, numClients):
		clients = ClosedLoopClient(sim, lb)
	
	sim.run()
