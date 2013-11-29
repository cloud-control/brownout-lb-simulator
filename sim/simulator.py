#!/usr/bin/env python
from __future__ import division, print_function

from collections import defaultdict, deque
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

def avg(a):
	if len(a) == 0:
		return float('nan')
	return sum(a)/len(a)

## Simulation kernel.
# Implements an event-driven simulator
class Simulator:
	## Constructor
	def __init__(self):
		## events indexed by time
		self.events = defaultdict(lambda: set())
		## reverse index from event handlers to time index, to allow easy update
		self.whatToTime = {}
		## current simulation time
		self.now = 0.0
		## cache of open file descriptors: for each issuer, this dictionary maps to a file descriptor
		self.outputFiles = {}

	## Adds a new event
	# @param delay non-negative float representing in how much time should the event be triggered
	# Can be zero, in which case the simulator will trigger the event a bit later, at the current
	# simulation time
	# @param what Event handler, can be a function, class method or lambda
	# @see Callable
	def add(self, delay, what):
		self.events[self.now + delay].add(what)
		self.whatToTime[what] = self.now + delay

	## Update an existing event or add a new event
	# @param delay in how much time should the event be triggered
	# @param what Callable to call for handling this event. Can be a function, class method or lambda
	# @note Deletes the previously existing event that is handled by what.
	# The current implementation stores at most one such event.
	def update(self, delay, what):
		if what in self.whatToTime:
			oldTime = self.whatToTime[what]
			events = self.events[oldTime]
			events.remove(what)
			if len(events) == 0:
				del self.events[oldTime]
			del self.whatToTime[what]
		self.add(delay, what)

	## Run the simulation
	# @param until time limit to stop simulation
	def run(self, until = 2000):
		numEvents = 0
		while self.events:
			prevNow = sim.now
			self.now = min(self.events)
			if int(prevNow / 100) < int(sim.now / 100):
				sim.log(self, "progressing, handled {0} events", numEvents)
			events = self.events[self.now]
			event = events.pop()
			del self.whatToTime[event]
			if len(events) == 0:
				del self.events[self.now]

			if self.now > until:
				return
			event()
			numEvents += 1
		self.log(self, "Handled {0} events", numEvents)

	## Log a simulation message.
	# This function is designed to simplify logging inside the simulator. It prints to standard error
	# the current simulation time, the stringified issuer of the message and the message itself.
	# Includes formatting similar to String.format or Logging.info.
	# @param issuer something that can be rendered as a string through str()
	# @param message the message, first input to String.format
	# @param *args,**kwargs additional arguments to pass to String.format
	def log(self, issuer, message, *args, **kwargs):
		print("{0:.6f}".format(self.now), str(issuer), message.format(*args, **kwargs), file = sys.stderr)

	## Output simulation data.
	# This function is designed to simplify outputting metrics from a simulated entity. It prints
	# the given line to a file, whose name is derived based on the issuer (currently "sim-{issuer}.csv").
	# @param issuer something that can be rendered as a string through str()
	# @param outputLine the line to output
	# @note outputLine is written verbatimly to the output file, plus a newline is added.
	def output(self, issuer, outputLine):
		if issuer not in self.outputFiles:
			outputFilename = 'sim-' + str(issuer) + '.csv'
			self.outputFiles[issuer] = open(outputFilename, 'w')
		outputFile = self.outputFiles[issuer]
		outputFile.write(outputLine + "\n")
		outputFile.flush() # kills performance, but reduces experimenter's impatience :D

	## Pretty-print the simulator kernel's name
	def __str__(self):
		return "kernel"

## Represents a request sent to an entity, waiting for a reply.
# @note If a request need to travers an entity, a <b>new</b> request should be created, poiting
# to the original request.
class Request:
	## Variable used for giving IDs to requests for pretty-printing
	lastRequestId = 1
	
	## Constructor
	def __init__(self):
		## ID of this request for pretty-printing
		self.requestId = Request.lastRequestId
		Request.lastRequestId += 1

	## Pretty-printer
	def __str__(self):
		return str(self.requestId)

## Represents a brownout compliant server.
# Current implementation simulates processor-sharing with an infinite number of concurrent requests
# and a fixed time-slice.
class Server:
	## Variable used for giving IDs to servers for pretty-printing
	lastServerId = 1

	## Constructor.
	# @param sim Simulator to attach the server to
	# @param serviceTimeY time to service one request with optional content
	# @param serviceTimeN time to service one request without optional content
	# @param timeSlice time slice; a request longer that this will observe context-switching
	# @param initialTheta initial dimmer value
	# @param controlPeriod control period of brownout controller
	# @note The constructor adds an event into the simulator
	def __init__(self, sim, serviceTimeY = 0.07, serviceTimeN = 0.001, \
			initialTheta = 0.5, controlPeriod = 5, timeSlice = 0.01):
		self.timeSlice = timeSlice
		self.serviceTimeY = serviceTimeY # service time with recommender system
		self.serviceTimeN = serviceTimeN # and without it
		self.controlPeriod = controlPeriod # second
		self.setPoint = 1 # second
		self.RLS_P = 1000 # initialization for the RLS estimator
		self.RLS_forgetting = 0.2
		self.alpha = 1
		self.pole = 0.9
		self.name = 'server' + str(Server.lastServerId)
		Server.lastServerId += 1

		self.sim = sim
		self.theta = initialTheta
		self.sim.add(0, lambda: self.runControlLoop())
		self.latestLatencies = []
		self.activeRequests = deque()

	## Runs the control loop.
	def runControlLoop(self):
		if self.latestLatencies:
			serviceTime = max(self.latestLatencies)
			serviceLevel = self.theta

			# choice of the estimator:
			# ------- bare estimator
			# self.alpha = serviceTime / serviceLevel # very rough estimate
			# ------- RLS estimation algorithm
			intermediateAlpha = serviceTime - self.alpha*self.theta
			g = self.RLS_P * self.theta * 1/(self.RLS_forgetting + self.theta*self.RLS_P*self.theta)
        		self.RLS_P = (1/self.RLS_forgetting) * self.RLS_P - g*self.theta*(1/self.RLS_forgetting)*self.RLS_P
			self.alpha = self.alpha + intermediateAlpha * g
			# end of the estimator - in the end self.alpha should be set
	
			# NOTE: control knob allowing to smooth service times
			# To enable this, you *must* add a new state variable (alpha) to the controller.
			#alpha = 0.5 * alpha + 0.5 * serviceTime / previousServiceLevel # very rough estimate
			error = self.setPoint - serviceTime
			# NOTE: control knob allowing slow increase
			if error > 0:
				error *= 0.1
			serviceLevel = serviceLevel + (1 / self.alpha) * (1 - self.pole) * error

			# saturation, service level is a probability
			serviceLevel = max(serviceLevel, 0.0)
			serviceLevel = min(serviceLevel, 1.0)

			# saturation, it's a probability
			self.theta = min(max(serviceLevel, 0.0), 1.0)
			#self.sim.log(self, "Measured maximum latency {1:.3f}, new theta {0:.2f}", \
			#	self.theta, serviceTime)
		
			valuesToOutput = [ self.sim.now, avg(self.latestLatencies), max(self.latestLatencies), self.theta ]
			self.sim.output(self, ','.join(["{0:.5f}".format(value) \
				for value in valuesToOutput]))

			self.latestLatencies = []

		# Re-run later
		self.sim.add(self.controlPeriod, lambda: self.runControlLoop())

	## Tells the server to serve a request.
	# @param request request to serve
	# @note When request completes, request.onCompleted() is called. The following attributes are added to the request:
	# <ul>
	#   <li>theta, the current dimmer value</li>
	#   <li>arrivel, time at which the request was first <b>scheduled</b>.
	#     May be arbitrary later than when request() was called</li>
	#   <li>completion, time at which the request finished</li>
	# </ul>
	def request(self, request):
		# Activate scheduler, if its not active
		if len(self.activeRequests) == 0:
			self.sim.add(0, self.onScheduleRequests)
		# Add request to list of active requests
		self.activeRequests.append(request)

	def onScheduleRequests(self):
		#self.sim.log(self, "scheduling")
		# Select next active request
		activeRequest = self.activeRequests.popleft()

		# Has this request been scheduled before?
		if not hasattr(activeRequest, 'remainingTime'):
			#self.sim.log(self, "request {0} entered the system", activeRequest)
			# Pick whether to serve it with optional content or not
			activeRequest.arrival = self.sim.now
			executeRecommender = random.random() <= self.theta
			activeRequest.theta = self.theta
			activeRequest.remainingTime = \
				self.serviceTimeY if executeRecommender else self.serviceTimeN

		# Schedule it to run for a bit
		timeToExecuteActiveRequest = min(self.timeSlice, activeRequest.remainingTime)
		activeRequest.remainingTime -= timeToExecuteActiveRequest

		# Will it finish?
		if activeRequest.remainingTime == 0:
			# Leave this request in front (onCompleted will pop it)
			self.activeRequests.appendleft(activeRequest)

			# Run onComplete when done
			self.sim.add(timeToExecuteActiveRequest, lambda: self.onCompleted(activeRequest))
			#self.sim.log(self, "request {0} will execute for {1} to completion", activeRequest, timeToExecuteActiveRequest)
		else:
			# Reintroduce it in the active request list at the end for round-robin scheduling
			self.activeRequests.append(activeRequest)

			# Re-run scheduler when time-slice has expired
			self.sim.add(timeToExecuteActiveRequest, lambda: self.onScheduleRequests())
			#self.sim.log(self, "request {0} will execute for {1} not to completion", activeRequest, timeToExecuteActiveRequest)

	def onCompleted(self, request):
		# Remove request from active list
		activeRequest = self.activeRequests.popleft()
		if activeRequest != request:
			raise Exception("Weird! Expected request {0} but got {1} instead".format(request, activeRequest))

		# And completed it
		request.completion = self.sim.now
		self.latestLatencies.append(request.completion - request.arrival)
		request.onCompleted()

		# Continue with scheduler
		if len(self.activeRequests) > 0:
			self.sim.add(0, self.onScheduleRequests)

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
		self.lastLatencies = []
		
		self.sim.add(0, self.runControlLoop)

	def addBackend(self, backend):
		self.backends.append(backend)
		self.lastThetas.append(self.initialTheta) # to be updated at onComplete
		self.lastLastThetas.append(self.initialTheta) # to be updated at onComplete
		self.lastLatencies.append([]) # to be updated at onComplete

		self.weights = [ 1.0 / len(self.backends) ] * len(self.backends)

	def request(self, request):
		#self.sim.log(self, "Got request {0}", request)
		generatedWeight = random.random()
		request.arrival = self.sim.now
		request.chosenBackendIndex = weightedChoice(zip(range(0, len(self.backends)), self.weights))
		newRequest = Request()
		newRequest.originalRequest = request
		newRequest.onCompleted = lambda: self.onCompleted(newRequest)
		#self.sim.log(self, "Directed request to {0}", newRequest.chosenBackendIndex)
		self.backends[request.chosenBackendIndex].request(newRequest)

	def onCompleted(self, request):
		# "Decapsulate"
		theta = request.theta
		request = request.originalRequest

		# Store stats
		request.completion = self.sim.now
		self.lastThetas[request.chosenBackendIndex] = theta
		self.lastLatencies[request.chosenBackendIndex].append(request.completion - request.arrival)
		
		# Call original onCompleted
		request.onCompleted()

	def runControlLoop(self):
		self.weights = map(lambda x: max(x[0] + x[1] - x[2], 0.01), \
			zip(self.weights, self.lastThetas, self.lastLastThetas))
		preNormalizedSumOfWeights = sum(self.weights)
		self.weights = map(lambda x: x / preNormalizedSumOfWeights, self.weights)

		self.sim.add(self.controlPeriod, self.runControlLoop)

		valuesToOutput = [ self.sim.now ] + self.weights + self.lastThetas + \
			[ avg(latencies) for latencies in self.lastLatencies ] + \
			[ max(latencies + [0]) for latencies in self.lastLatencies ]
		self.sim.output(self, ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))
		
		self.lastLastThetas = self.lastThetas[:]
		self.lastLatencies = [ [] for b in self.backends ]

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

		self.numCompletedRequests = 0
		self.active = True

	def issueRequest(self):
		if not self.active:
			return
		request = Request()
		request.onCompleted = lambda: self.onCompleted(request)
		#self.sim.log(self, "Requested {0}", request)
		self.server.request(request)

	def onCompleted(self, request):
		thinkTime = random.expovariate(1.0 / self.averageThinkTime)
		self.sim.add(thinkTime, self.issueRequest)
		#self.sim.log(self, "Thinking for {0}", thinkTime)
		self.numCompletedRequests += 1
	
	def __str__(self):
		return self.name

if __name__ == "__main__":
	numClients = 50
	serverControlPeriod = 5

	random.seed(1)
	sim = Simulator()
	server1 = Server(sim, controlPeriod = serverControlPeriod)
	server2 = Server(sim, controlPeriod = serverControlPeriod, serviceTimeY = 0.07 * 2, serviceTimeN = 0.001 * 2)
	server3 = Server(sim, controlPeriod = serverControlPeriod, serviceTimeY = 0.07 * 3, serviceTimeN = 0.001 * 3)

	lb = LoadBalancer(sim, controlPeriod = 1)
	lb.addBackend(server1)
	lb.addBackend(server2)
	lb.addBackend(server3)

	clients = []
	def addClients(numClients):
		for i in range(0, numClients):
			clients.append(ClosedLoopClient(sim, lb))

	def removeClients(numClients):
		for i in range(0, numClients):
			client = clients.pop()
			client.active = False

	sim.add(   0, lambda: addClients(numClients))
	sim.add( 500, lambda: addClients(numClients))
	sim.add(1000, lambda: removeClients(int(numClients*1.5)))
	sim.add(1500, lambda: addClients(int(numClients/2)))
	
	sim.run()

