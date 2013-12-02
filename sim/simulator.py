#!/usr/bin/env python
from __future__ import division, print_function

## @mainpage
# Documentation for the brownout load-balancer simulator. If confused, start with the @ref simulator namespace.

from collections import defaultdict, deque
import heapq
import Queue
import random
import math
import sys

## @package simulator Main simulator namespace

## Randomly picks an item from several choices, as given by the attached weights.
# Sum of weight must equal 1.
# Example: @code weightedChoice([('a', 0.1), ('b', 0.9)]) @endcode
#
# @param choices list of pairs to choose from; first item in pair is choice, second is weight
def weightedChoice(choices):
	total = sum(w for c, w in choices)
	r = random.uniform(0, total)
	upto = 0
	for c, w in choices:
		if upto + w > r:
			return c
		upto += w
	assert False, "Shouldn't get here"

## Computes average
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
			prevNow = self.now
			self.now = min(self.events)
			if int(prevNow / 100) < int(self.now / 100):
				self.log(self, "progressing, handled {0} events", numEvents)
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
# @note If a request needs to traverse an entity, a <b>new</b> request should be created, pointing
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
	# @param serviceTimeYVariance varince in service-time with optional content
	# @param serviceTimeNVariance varince in service-time without optional content
	# @param minimumServiceTime minimum service-time (despite variance)
	# @param timeSlice time slice; a request longer that this will observe context-switching
	# @param initialTheta initial dimmer value
	# @param controlPeriod control period of brownout controller
	# @note The constructor adds an event into the simulator
	def __init__(self, sim, serviceTimeY = 0.07, serviceTimeN = 0.001, \
			initialTheta = 0.5, controlPeriod = 5, timeSlice = 0.01, \
			serviceTimeYVariance = 0.01, serviceTimeNVariance = 0.001,
			minimumServiceTime = 0.0001):
		## time slice for scheduling requests (server model parameter)
		self.timeSlice = timeSlice
		## service time with optional content (server model parameter)
		self.serviceTimeY = serviceTimeY
		## service time without optional content (server model parameter)
		self.serviceTimeN = serviceTimeN
		## service time variance with optional content (server model parameter)
		self.serviceTimeYVariance = serviceTimeYVariance
		## service time variance without optional content (server model parameter)
		self.serviceTimeNVariance = serviceTimeNVariance
		## minimum service time, despite variance (server model parameter)
		self.minimumServiceTime = minimumServiceTime
		## list of active requests (server model variable)
		self.activeRequests = deque()

		## control period (controller parameter)
		self.controlPeriod = controlPeriod # second
		## setpoint (controller parameter)
		self.setPoint = 1
		## initialization for the RLS estimator (controller variable)
		self.RLS_P = 1000
		## RLS forgetting factor (controller parameter)
		self.RLS_forgetting = 0.2
		## Current alpha (controller variable)
		self.alpha = 1
		## Pole (controller parameter)
		self.pole = 0.9
		## latencies measured during last control period (controller input)
		self.latestLatencies = []
		## dimmer value (controller output)
		self.theta = initialTheta

		## Server ID for pretty-printing
		self.name = 'server' + str(Server.lastServerId)
		Server.lastServerId += 1

		## Reference to simulator
		self.sim = sim
		self.sim.add(0, lambda: self.runControlLoop())

	## Runs the control loop.
	# Basically retrieves self.lastestLatencies and computes a new self.theta. Ask Martina for details. :P
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
	#   <li>arrival, time at which the request was first <b>scheduled</b>.
	#     May be arbitrary later than when request() was called</li>
	#   <li>completion, time at which the request finished</li>
	# </ul>
	def request(self, request):
		# Activate scheduler, if its not active
		if len(self.activeRequests) == 0:
			self.sim.add(0, self.onScheduleRequests)
		# Add request to list of active requests
		self.activeRequests.append(request)

	## Event handler for scheduling active requests.
	# This function is the core of the processor-sharing with time-slice model. This function is called
	# when "context-switching" occurs. There must be at most one such event registered in the simulation.
	# This function is invoked in the following cases:
	# <ul>
	#   <li>By request(), when the list of active requests was previously empty.</li>
	#   <li>By onCompleted(), to pick a new request to schedule</li>
	#   <li>By itself, when a request is preempted, i.e., context-switched</li>
	# </ul>
	def onScheduleRequests(self):
		#self.sim.log(self, "scheduling")
		# Select next active request
		activeRequest = self.activeRequests.popleft()

		# Has this request been scheduled before?
		if not hasattr(activeRequest, 'remainingTime'):
			#self.sim.log(self, "request {0} entered the system", activeRequest)
			# Pick whether to serve it with optional content or not
			activeRequest.arrival = self.sim.now
			activeRequest.withOptional = random.random() <= self.theta
			activeRequest.theta = self.theta

			serviceTime, variance = (self.serviceTimeY, self.serviceTimeYVariance) \
				if activeRequest.withOptional else (self.serviceTimeN, self.serviceTimeNVariance)

			activeRequest.remainingTime = \
				max(random.normalvariate(serviceTime, variance), self.minimumServiceTime)

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

	## Event handler for request completion.
	# Marks the request as completed, calls request.onCompleted() and calls onScheduleRequests() to
	# pick a new request to schedule.
	# @param request request that has received enough service time
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

	## Pretty-print server's ID
	def __str__(self):
		return str(self.name)

## Simulates a load-balancer.
# The load-balancer is assumed to take zero time for its decisions.
class LoadBalancer:
	## Constructor.
	# @param sim Simulator to attach to
	# @param controlPeriod control period
	# @param initialTheta initial dimmer value to consider before receiving any replies from a server
	def __init__(self, sim, controlPeriod = 1, initialTheta = 0.5):
		## control period (control parameter)
		self.controlPeriod = controlPeriod # second
		## initial value of measured theta (control initialization parameter)
		self.initialTheta = initialTheta

		## Simulator to which the load-balancer is attached
		self.sim = sim
		## list of back-end servers to which requests can be directed
		self.backends = []
		## weights determining how to load-balance requests (control output)
		self.weights = []
		## dimmer values measured during the previous control period (control input)
		self.lastThetas = []
		## dimmer values measured during before previous control period (control input)
		self.lastLastThetas = []
		## latencies measured during last control period (metric)
		self.lastLatencies = []
		## number of requests, with or without optional content, served since the load-balancer came online (metric)
		self.numRequests = 0
		## number of requests, with optional content, served since the load-balancer came online (metric)
		self.numRequestsWithOptional = 0
		
		# Launch control loop
		self.sim.add(0, self.runControlLoop)

	## Adds a new back-end server and initializes decision variables.
	# @param backend the server to add
	def addBackend(self, backend):
		self.backends.append(backend)
		self.lastThetas.append(self.initialTheta) # to be updated at onComplete
		self.lastLastThetas.append(self.initialTheta) # to be updated at onComplete
		self.lastLatencies.append([]) # to be updated at onComplete

		self.weights = [ 1.0 / len(self.backends) ] * len(self.backends)

	## Handles a request.
	# @param request the request to handle
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

	## Handles request completion.
	# Stores piggybacked dimmer values and calls orginator's onCompleted() 
	def onCompleted(self, request):
		# "Decapsulate"
		self.numRequests += 1
		if request.withOptional: self.numRequestsWithOptional += 1
		theta = request.theta
		request = request.originalRequest

		# Store stats
		request.completion = self.sim.now
		self.lastThetas[request.chosenBackendIndex] = theta
		self.lastLatencies[request.chosenBackendIndex].append(request.completion - request.arrival)
		
		# Call original onCompleted
		request.onCompleted()

	## Run control loop.
	# Takes as input the dimmers and computes new weights. Also outputs CVS-formatted statistics through the
	# Simulator's output routine.
	def runControlLoop(self):
		self.weights = map(lambda x: max(x[0] + x[1] - x[2], 0.01), \
			zip(self.weights, self.lastThetas, self.lastLastThetas))
		preNormalizedSumOfWeights = sum(self.weights)
		self.weights = map(lambda x: x / preNormalizedSumOfWeights, self.weights)

		self.sim.add(self.controlPeriod, self.runControlLoop)

		valuesToOutput = [ self.sim.now ] + self.weights + self.lastThetas + \
			[ avg(latencies) for latencies in self.lastLatencies ] + \
			[ max(latencies + [0]) for latencies in self.lastLatencies ] + \
			[ self.numRequests, self.numRequestsWithOptional ]
		self.sim.output(self, ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))
		
		self.lastLastThetas = self.lastThetas[:]
		self.lastLatencies = [ [] for b in self.backends ]

	## Pretty-print load-balancer's name.
	def __str__(self):
		return "lb"

## Simulates a closed-loop client.
# The client waits for a request to complete before issuing a new one.
class ClosedLoopClient:
	## Variable used for giving IDs for pretty-printing
	lastClientId = 1

	## Constructor.
	# @param sim Simulator to attach client to
	# @param server server-like entity to which requests are sent
	# @param thinkTime average think-time between issuing consecutive requests
	def __init__(self, sim, server, thinkTime = 1):
		## average think-time (model parameter)
		self.averageThinkTime = thinkTime
		## ID of this client used for pretty-printing
		self.name = 'client' + str(ClosedLoopClient.lastClientId)
		ClosedLoopClient.lastClientId += 1

		## simulator to which the client is attached
		self.sim = sim
		## server to which requests are issued
		self.server = server

		## Variable that measure the number of requests completed for this user (metric)
		self.numCompletedRequests = 0
		## Variable used to deactive the client
		self.active = True
		
		# Launch client in the thinking phase
		self.sim.add(0, lambda: self.onCompleted(None))

	## Issues a new request to the server.
	def issueRequest(self):
		if not self.active:
			return
		request = Request()
		request.onCompleted = lambda: self.onCompleted(request)
		#self.sim.log(self, "Requested {0}", request)
		self.server.request(request)

	## Called when a request completes
	# @param request the request that has been completed
	def onCompleted(self, request):
		thinkTime = random.expovariate(1.0 / self.averageThinkTime)
		self.sim.add(thinkTime, self.issueRequest)
		#self.sim.log(self, "Thinking for {0}", thinkTime)
		self.numCompletedRequests += 1

	## Deactive this client.
	# The client will not issue any more requests and no new simulator events are created. Hence,
	# the object can be garbage-collected.
	def deactivate(self):
		self.active = False
	
	## Pretty-print client's name
	def __str__(self):
		return self.name

## Entry-point for simulator.
# Setups up all entities, then runs simulation.
def main():
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
			client.deactivate()

	sim.add(   0, lambda: addClients(numClients))
	sim.add( 500, lambda: addClients(numClients))
	sim.add(1000, lambda: removeClients(int(numClients*1.5)))
	sim.add(1500, lambda: addClients(int(numClients/2)))
	
	sim.run()

if __name__ == "__main__":
	main()
