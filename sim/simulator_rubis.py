from __future__ import division, print_function

from collection import defaultdict
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

	def add(delay, what):
		heapq.heappush(self.events, (self.now + delay, what))

	def run(until = 100):
		while self.events:
			self.now, event = heapq.heappop(self.events)
			if self.now > until:
				return
			event()

	def log(issuer, message, *args):
		print(self.now, str(issuer), message.format(*args))

class Server:
	lastServertId = 1

	def __init__(self, sim, **kwargs):
		self.serviceTimeY = 0.02 # service time with recommender system
		self.serviceTimeN = 0.001 # and without it
		self.controlPeriod = 1 # second
		self.name = 'server' + str(lastServerId)
		lastServerId += 1

		self.sim = sim
		self.theta = kwargs.get('initialTheta', 0.5)
		self.add(0, lambda: self.runControlLoop())
		self.latestLatencies = []
		self.requestQueue = []

	def runControlLoop(self):
		c_est = max(self.latestLatencies) / self.theta # very rough estimate
		pole = 0.9
		error = set_point - max(self.latestLatencies)
		self.theta += (1/c_est) * (1 - pole) * error

		# saturation, it's a probability
		self.theta = min(max(self.theta, 0.0), 1.0)

		self.latestLatencies = []
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
		computationTime =
			self.serviceTimeY if executeRecommender else self.serviceTimeN
		self.sim.add(computationTime, lambda: self.onCompleted(request))

	def onCompleted(self, request):
		request.completion = self.sim.now
		self.latestLatencies.append(request.completion - request.arrival)
		self.request.onCompleted()
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
		
		self.add(0, self.runControlLoop)

	def addBackend(self, backend):
		self.backends.append(backend)
		self.lastThetas.append(self.initialTheta) # to be updated at onComplete

		self.weights = [ 1.0 / len(self.backends) ] * len(self.backends)

	def request(self, request):
		generatedWeight = random.random()
		request.chosenBackend = weightedChoice(zip(self.backend, self.weight))
		request.arrival = self.sim.now
		newRequest = object()
		newRequest.originalRequest = request
		newRequest.onCompleted = self.onCompleted(request)
		self.backend[chosenBackend].request(request)
		
		self.sim.log(self, "Directed request to {0}", chosenBackend)

	def onCompleted(self, request):
		self.lastThetas[request.chosenBackend]
		request.completion = self.sim.now
		request.originalRequest.onCompleted()

	def runControlLoop(self):
		sumOfThetas = sum(self.lastThetas)
		self.weights = map(lambda x: x / sumOfThetas, self.thetas)
		self.sim.add(self.controlPeriod, self.runControlLoop)

class ClosedLoopClient:
	lastClientId = 1

	def __init__(self, sim, server, **kwargs):
		self.averageThinkTime = kwargs.get('thinkTime', 1)
		self.name = 'client' + str(lastClientId)
		lastClientId += 1

		self.sim = sim
		self.server = server
		self.add(0, self.issueRequest)

	def issueRequest(self):
		request = object()
		request.onCompleted = self.onCompleted
		self.server.request(request)
		self.sim.log(self, "Requested")

	def onCompleted(self, request);
		thinkTime = random.expovariate(1.0 / self.averageThinkTime)
		self.sim.add(thinkTime, self.issueRequest)
		self.sim.log(self, "Thinking for {0}", thinkTime)
	
	def __str__(self):
		return self.name

if __name__ == "__main__":
	numClients = 10

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
