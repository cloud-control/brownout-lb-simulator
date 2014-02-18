#!/usr/bin/env python
from __future__ import division, print_function

## @mainpage
# Documentation for the brownout load-balancer simulator. If confused, start
# with the @ref simulator namespace.

from collections import defaultdict, deque
import numpy as np
from cvxopt import solvers, matrix, spdiag, log
import cvxopt
import os
import random
import sys
import math
import argparse

## @package simulator Main simulator namespace

## Randomly picks an item from several choices, as given by the attached
# weights. Sum of weight must equal 1.
# Example: @code weightedChoice([('a', 0.1), ('b', 0.9)]) @endcode
#
# @param choiceWeightPairs list of pairs to choose from; first item in pair is
# choice, second is weight
def weightedChoice(choiceWeightPairs):
	totalWeight = sum(weight for choice, weight in choiceWeightPairs)
	rnd = random.uniform(0, totalWeight)
	upto = 0
	for choice, weight in choiceWeightPairs:
		if upto + weight > rnd:
			return choice
		upto += weight
	assert False, "Shouldn't get here"

## Computes average
# @param numbers list of number to compute average for
# @return average or NaN if list is empty
def avg(numbers):
	if len(numbers) == 0:
		return float('nan')
	return sum(numbers)/len(numbers)

## Computes maximum
# @param numbers list of number to compute maximum for
# @return maximum or NaN if list is empty
# @note Similar to built-in function max(), but returns NaN instead of throwing
# exception when list is empty
def maxOrNan(numbers):
	if len(numbers) == 0:
		return float('nan')
	return max(numbers)

## Normalize a list, so that the sum of all elements becomes 1
# @param numbers list to normalize
# @return normalized list
def normalize(numbers):
	if len(numbers) == 0:
		# Nothing to do
		return [ ]
	
	s = sum(numbers)
	if s == 0:
	# How to normalize a zero vector is a matter of much debate
		return [ float('nan') ] * len(numbers)
	return [ n / s for n in numbers ]

## Simulation kernel.
# Implements an event-driven simulator
class Simulator:
	## Constructor
	def __init__(self, outputDirectory = '.'):
		## events indexed by time
		self.events = defaultdict(list)
		## reverse index from event handlers to time index, to allow easy update
		self.whatToTime = {}
		## current simulation time
		self.now = 0.0
		## cache of open file descriptors: for each issuer, this dictionary maps
		# to a file descriptor
		self.outputFiles = {}
		## output directory
		self.outputDirectory = outputDirectory
		self.optionalOn = 0
		self.optionalOff = 0
		self.avgServiceTime = 0
		self.stdServiceTime = 0

	## Adds a new event
	# @param delay non-negative float representing in how much time should the
	# event be triggered. Can be zero, in which case the simulator will trigger
	# the event a bit later, at the current simulation time.
	# @param what Event handler, can be a function, class method or lambda
	# @see Callable
	def add(self, delay, what):
		self.events[self.now + delay].append(what)
		self.whatToTime[what] = self.now + delay

	## Update an existing event or add a new event
	# @param delay in how much time should the event be triggered
	# @param what Callable to call for handling this event. Can be a function,
	# class method or lambda
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
			#if int(prevNow / 100) < int(self.now / 100):
			#	self.log(self, "progressing, handled {0} events", numEvents)
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
	# This function is designed to simplify logging inside the simulator. It
	# prints to standard error
	# the current simulation time, the stringified issuer of the message and the
	# message itself. Includes formatting similar to String.format or
	# Logging.info.
	# @param issuer something that can be rendered as a string through str()
	# @param message the message, first input to String.format
	# @param *args,**kwargs additional arguments to pass to String.format
	def log(self, issuer, message, *args, **kwargs):
		print("{0:.6f}".format(self.now), str(issuer), \
			message.format(*args, **kwargs), file = sys.stderr)

	## Output simulation data.
	# This function is designed to simplify outputting metrics from a simulated
	# entity. It prints the given line to a file, whose name is derived based on
	# the issuer (currently "sim-{issuer}.csv").
	# @param issuer something that can be rendered as a string through str()
	# @param outputLine the line to output
	# @note outputLine is written verbatimly to the output file, plus a newline
	# is added.
	def output(self, issuer, outputLine):
		if issuer not in self.outputFiles:
			outputFilename = 'sim-' + str(issuer) + '.csv'
			outputFilename = os.path.join(self.outputDirectory, outputFilename)
			self.outputFiles[issuer] = open(outputFilename, 'w')
		outputFile = self.outputFiles[issuer]
		outputFile.write(outputLine + "\n")

		# kills performance, but reduces experimenter's impatience :D
		outputFile.flush()

	## Pretty-print the simulator kernel's name
	def __str__(self):
		return "kernel"

## Represents a request sent to an entity, waiting for a reply. This class has
# little logic, its use is basically as a dictionary.
# @note If a request needs to traverse an entity, a <b>new</b> request should be
# created, pointing to the original request.
class Request(object):
	# pylint: disable=R0903

	## Variable used for giving IDs to requests for pretty-printing
	lastRequestId = 1
	## List of allowed attributes (improves performance and reduces errors)
	__slots__ = ('requestId', 'arrival', 'completion', 'onCompleted', \
		'originalRequest', 'theta', 'withOptional', 'chosenBackendIndex',
		'remainingTime')
	
	## Constructor
	def __init__(self):
		## ID of this request for pretty-printing
		self.requestId = Request.lastRequestId
		Request.lastRequestId += 1
		## Callable to call when request has completed
		self.onCompleted = lambda: ()
		## Request originating this request
		self.originalRequest = None


	## Pretty-printer
	def __str__(self):
		return str(self.requestId)

## Represents a brownout compliant server.
# Current implementation simulates processor-sharing with an infinite number of
# concurrent requests and a fixed time-slice.
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
	# @param timeSlice time slice; a request longer that this will observe
	# context-switching
	# @param initialTheta initial dimmer value
	# @param controlPeriod control period of brownout controller (0 = disabled)
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
		self.rlsP = 1000
		## RLS forgetting factor (controller parameter)
		self.rlsForgetting = 0.95
		## Current alpha (controller variable)
		self.alpha = 1
		## Pole (controller parameter)
		self.pole = 0.99
		## latencies measured during last control period (controller input)
		self.latestLatencies = []
		## dimmer value (controller output)
		self.theta = initialTheta

		## The amount of time this server is active. Useful to compute utilization
		# Since we are in a simulator, this value is hard to use correctly. Use getActiveTime() instead.
		self.__activeTime = 0
		## The time when the server became last active (None, not currently active)
		self.__activeTimeStarted = None
		## Value used to compute utilization
		self.lastActiveTime = 0

		## Server ID for pretty-printing
		self.name = 'server' + str(Server.lastServerId)
		Server.lastServerId += 1

		## Reference to simulator
		self.sim = sim
		if self.controlPeriod > 0:
			self.sim.add(0, self.runControlLoop)

	## Compute the (simulated) amount of time this server has been active.
	# @note In a real OS, the active time would be updated at each context switch.
	# However, this is a simulation, therefore, in order not to waste time on
	# simulating context-switches, we compute this value when requested, as if it
	# were continuously update.
	def getActiveTime(self):
		ret = self.__activeTime
		if self.__activeTimeStarted is not None:
			ret += self.sim.now - self.__activeTimeStarted
		return ret

	## Runs the control loop.
	# Basically retrieves self.lastestLatencies and computes a new self.theta.
	# Ask Martina for details. :P
	def runControlLoop(self):
		if self.latestLatencies:
			# Possible choices: max or avg latency control
			# serviceTime = avg(self.latestLatencies) # avg latency
			# serviceTime = max(self.latestLatencies) # max latency
			serviceTime = np.percentile(self.latestLatencies, 95) # 95 percentile
			serviceLevel = self.theta

			# choice of the estimator:
			# ------- bare estimator
			# self.alpha = serviceTime / serviceLevel # very rough estimate
			# ------- RLS estimation algorithm
			a = self.rlsP*serviceLevel
			g = 1 / (serviceLevel*a + self.rlsForgetting)
			k = g*a
			e = serviceTime - serviceLevel*self.alpha
			self.alpha = self.alpha + k*e
			self.rlsP  = (self.rlsP - g * a*a) / self.rlsForgetting
			# end of the estimator - in the end self.alpha should be set
			
			error = self.setPoint - serviceTime
			# NOTE: control knob allowing slow increase
			#if error > 0:
			#	error *= 0.1
			variation = (1 / self.alpha) * (1 - self.pole) * error
			serviceLevel += self.controlPeriod * variation

			# saturation, it's a probability
			self.theta = min(max(serviceLevel, 0.0), 1.0)
		
		# Compute utilization
		utilization = (self.getActiveTime() - self.lastActiveTime) / self.controlPeriod
		self.lastActiveTime = self.getActiveTime()

		# Report
		valuesToOutput = [ \
			self.sim.now, \
			avg(self.latestLatencies), \
			maxOrNan(self.latestLatencies), \
			self.theta, \
			utilization, \
		]
		self.sim.output(self, ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))

		# Re-run later
		self.latestLatencies = []
		self.sim.add(self.controlPeriod, self.runControlLoop)

	## Tells the server to serve a request.
	# @param request request to serve
	# @note When request completes, request.onCompleted() is called.
	# The following attributes are added to the request:
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
	# This function is the core of the processor-sharing with time-slice model.
	# This function is called when "context-switching" occurs. There must be at
	# most one such event registered in the simulation.
	# This function is invoked in the following cases:
	# <ul>
	#   <li>By request(), when the list of active requests was previously empty.
	#   </li>
	#   <li>By onCompleted(), to pick a new request to schedule</li>
	#   <li>By itself, when a request is preempted, i.e., context-switched</li>
	# </ul>
	def onScheduleRequests(self):
		#self.sim.log(self, "scheduling")
		# Select next active request
		activeRequest = self.activeRequests.popleft()
		
		# Track utilization
		if self.__activeTimeStarted is None:
			self.__activeTimeStarted = self.sim.now

		# Has this request been scheduled before?
		if not hasattr(activeRequest, 'remainingTime'):
			#self.sim.log(self, "request {0} entered the system", activeRequest)
			# Pick whether to serve it with optional content or not
			activeRequest.arrival = self.sim.now
			activeRequest.withOptional = random.random() <= self.theta
			activeRequest.theta = self.theta

			serviceTime, variance = (self.serviceTimeY, self.serviceTimeYVariance) \
				if activeRequest.withOptional else \
				(self.serviceTimeN, self.serviceTimeNVariance)

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
			self.sim.add(timeToExecuteActiveRequest, \
				lambda: self.onCompleted(activeRequest))
			#self.sim.log(self, "request {0} will execute for {1} to completion", \
			#	activeRequest, timeToExecuteActiveRequest)
		else:
			# Reintroduce it in the active request list at the end for
			# round-robin scheduling
			self.activeRequests.append(activeRequest)

			# Re-run scheduler when time-slice has expired
			self.sim.add(timeToExecuteActiveRequest, self.onScheduleRequests)
			#self.sim.log(self, "request {0} will execute for {1} not to completion",\
			#	activeRequest, timeToExecuteActiveRequest)

	## Event handler for request completion.
	# Marks the request as completed, calls request.onCompleted() and calls
	# onScheduleRequests() to pick a new request to schedule.
	# @param request request that has received enough service time
	def onCompleted(self, request):
		# Track utilization
		self.__activeTime += self.sim.now - self.__activeTimeStarted
		self.__activeTimeStarted = None

		# Remove request from active list
		activeRequest = self.activeRequests.popleft()
		if activeRequest != request:
			raise Exception("Weird! Expected request {0} but got {1} instead". \
				format(request, activeRequest))

		# And completed it
		request.completion = self.sim.now
		self.latestLatencies.append(request.completion - request.arrival)
		request.onCompleted()

		# Report
		valuesToOutput = [ \
			self.sim.now, \
			request.completion - request.arrival, \
		]
		self.sim.output(str(self)+'-rt', ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))

		# Continue with scheduler
		if len(self.activeRequests) > 0:
			self.sim.add(0, self.onScheduleRequests)

	## Pretty-print server's ID
	def __str__(self):
		return str(self.name)

## Simulates a link with latency
class Link:
	## Constructor.
	# @param sim instance of a simulator.
	# @param server server to direct incoming requests to
	# @param delay delay (in seconds) introduced by this link
	def __init__(self, sim, server, delay = 0.01):
		## destination server
		self.server = server
		## simulator instance
		self.sim = sim
		## delay (in seconds) that the link introduces
		self.delay = delay

	## Handles a request.
	# @param request the request to handle
	def request(self, request):
		newRequest = Request()
		newRequest.originalRequest = request
		newRequest.onCompleted = lambda: self.onCompleted(newRequest)
		self.sim.add(self.delay, lambda: self.server.request(newRequest))

	## Handles a completed request.
	# @param request the request to handle
	def onCompleted(self, request):
		originalRequest = request.originalRequest
		# XXX: decapsulation could/should be improved
		originalRequest.withOptional = request.withOptional
		originalRequest.theta = request.theta
		self.sim.add(self.delay, lambda: originalRequest.onCompleted())

## Simulates a load-balancer.
# The load-balancer is assumed to take zero time for its decisions.
class LoadBalancer:
	## Constructor.
	# @param sim Simulator to attach to
	# @param controlPeriod control period
	# @param initialTheta initial dimmer value to consider before receiving any
	# replies from a server
	def __init__(self, sim, controlPeriod = 1, initialTheta = 0.5):
		## control period (control parameter)
		self.controlPeriod = controlPeriod # second
		## initial value of measured theta (control initialization parameter)
		self.initialTheta = initialTheta
		## what algorithm to use
		self.algorithm = 'theta-diff'

		## Simulator to which the load-balancer is attached
		self.sim = sim
		## list of back-end servers to which requests can be directed
		self.backends = []
		## weights determining how to load-balance requests (control output)
		self.weights = []
		## last deviation of theta from the average (for equal-thetas)
		self.lastThetaErrors = []
		## dimmer values measured during the previous control period (control input)
		self.lastThetas = []
		## dimmer values measured during before previous control period
		# (control input)
		self.lastLastThetas = []
		## latencies measured during last control period (metric)
		self.lastLatencies = []
		self.lastLastLatencies = []
		## queue length of each replica (control input for SQF algorithm)
		self.queueLengths = []
		self.lastQueueLengths = []
		## number of requests, with or without optional content, served since
		# the load-balancer came online (metric)
		self.numRequests = 0
		self.lastNumRequests = 0
		## number of requests, with optional content, served since the
		# load-balancer came online (metric)
		self.numRequestsWithOptional = 0
		## number of requests served by each replica (metric).
		self.numRequestsPerReplica = []
		## number of requests served by each replica before the last control period (metric).
		self.numLastRequestsPerReplica = []
		self.iteration = 1
		## average response time of each replica (control input for FRF-EWMA algorithm)
		self.ewmaResponseTime = []
		## number of sample to use for computing average response time (parameter for FRF-EWMA algorithm)
		self.ewmaNumSamples = 10
		## average service time and standard deviation for performance indexes
		self.averageServiceTime = 0
		self.intermediateForVariance = 0 	
		self.stdServiceTime = 0
		## for the ctl-simplify algorithm
		self.ctlRlsP = []
		self.ctlAlpha = []
		
		# Launch control loop
		self.sim.add(0, self.runControlLoop)

	## Adds a new back-end server and initializes decision variables.
	# @param backend the server to add
	def addBackend(self, backend):
		self.backends.append(backend)
		self.lastThetaErrors.append(0)
		self.lastThetas.append(self.initialTheta) # to be updated at onComplete
		self.lastLastThetas.append(self.initialTheta) # to be updated at onComplete
		self.lastLatencies.append([]) # to be updated at onComplete
		self.lastLastLatencies.append([])
		self.queueLengths.append(0) # to be updated in request and onComplete
		self.lastQueueLengths.append(0)
		self.numRequestsPerReplica.append(0) # to be updated in request
		self.numLastRequestsPerReplica.append(0) # to be updated in runControlLoop
		self.ewmaResponseTime.append(0) # to be updated in onComplete
		## for ctl-simplify
		self.ctlRlsP.append(1000)
		self.ctlAlpha.append(1)

		self.weights = [ 1.0 / len(self.backends) ] * len(self.backends)

	## Handles a request.
	# @param request the request to handle
	def request(self, request):
		#self.sim.log(self, "Got request {0}", request)
		request.arrival = self.sim.now
		if self.algorithm in [ 'weighted-RR', 'theta-diff', 'theta-diff-plus', 'equal-thetas', 'optimization', 'ctl-simplify' ]:
			request.chosenBackendIndex = \
				weightedChoice(zip(range(0, len(self.backends)), self.weights))
		elif self.algorithm == 'random':
			# round robin
			request.chosenBackendIndex = \
				random.choice(range(0, len(self.backends)))
		elif self.algorithm == 'RR':
			# round robin
			request.chosenBackendIndex = \
				(self.numRequests % len(self.backends)) - 1
		elif self.algorithm == 'SQF':
			# choose replica with shortest queue
			request.chosenBackendIndex = \
				min(range(0, len(self.queueLengths)), \
				key = lambda i: self.queueLengths[i])
		elif self.algorithm == 'SQF-plus':
			# choose replica with shortest queue
			minIndices = [i for i, x in enumerate(self.queueLengths) if x == min(self.queueLengths)]
			if len(minIndices) == 1:
				request.chosenBackendIndex = minIndices[0]
			else:
				dimmers = [self.lastThetas[i] for i in minIndices]
				maxDimmerIndex = dimmers.index(max(dimmers))
				request.chosenBackendIndex = minIndices[maxDimmerIndex]
		elif self.algorithm == '2RC':
			maxlat = [max(x) if x else 0 for x in self.lastLatencies]
			if len(self.backends) == 1:
				request.chosenBackendIndex = 0
			# randomly select two backends and send it to the one with lowest latency
			else:
				backends = set(range(0, len(self.backends)))
				randomlychosen = random.sample(backends, 2)
				if maxlat[randomlychosen[0]] > maxlat[randomlychosen[1]]:
					request.chosenBackendIndex = randomlychosen[1]
				else:
					request.chosenBackendIndex = randomlychosen[0]
		elif self.algorithm == 'FRF':
			# choose replica with minimum latency
			maxlat = [max(x) if x else 0 for x in self.lastLatencies]
			request.chosenBackendIndex = \
				maxlat.index(min(maxlat))
		elif self.algorithm == 'FRF-EWMA':
			# choose replica with minimum EWMA latency
			#self.sim.log(self, "EWMA RT {0}", self.ewmaResponseTime)
			request.chosenBackendIndex = \
				min(range(0, len(self.backends)), \
				key = lambda i: self.ewmaResponseTime[i])
		elif self.algorithm == 'predictive':
			maxlat = np.array([max(x) if x else 0 for x in self.lastLatencies])
			maxlatLast = np.array([max(x) if x else 0 for x in self.lastLastLatencies])
			wlat = 0.2
			wqueue = 0.8
			points = wlat*(maxlat - maxlatLast) + wqueue*(np.array(self.queueLengths) - np.array(self.lastQueueLengths))
			# choose replica with shortest queue
			request.chosenBackendIndex = \
				min(range(0, len(points)), \
				key = lambda i: points[i])
		else:
			raise Exception("Unknown load-balancing algorithm " + self.algorithm)
			
		newRequest = Request()
		newRequest.originalRequest = request
		newRequest.onCompleted = lambda: self.onCompleted(newRequest)
		#self.sim.log(self, "Directed request to {0}", request.chosenBackendIndex)
		self.queueLengths[request.chosenBackendIndex] += 1
		self.numRequestsPerReplica[request.chosenBackendIndex] += 1
		self.backends[request.chosenBackendIndex].request(newRequest)

	## Handles request completion.
	# Stores piggybacked dimmer values and calls orginator's onCompleted() 
	def onCompleted(self, request):
		# "Decapsulate"
		self.numRequests += 1
		if request.withOptional:
			self.sim.optionalOn += 1
			self.numRequestsWithOptional += 1
		else:
			self.sim.optionalOff += 1
		theta = request.theta
		request = request.originalRequest

		# Store stats
		request.completion = self.sim.now
		self.lastThetas[request.chosenBackendIndex] = theta
		self.lastLatencies[request.chosenBackendIndex].\
			append(request.completion - request.arrival)
		self.queueLengths[request.chosenBackendIndex] -= 1
		ewmaAlpha = 2 / (self.ewmaNumSamples + 1)
		self.ewmaResponseTime[request.chosenBackendIndex] = \
			ewmaAlpha * (request.completion - request.arrival) + \
			(1 - ewmaAlpha) * self.ewmaResponseTime[request.chosenBackendIndex]
	
		# Compute performance indexes
		serviceTime = request.completion - request.arrival
		delta = serviceTime - self.averageServiceTime
		self.averageServiceTime = self.averageServiceTime + delta / self.numRequests
		self.intermediateForVariance += delta * (serviceTime - self.averageServiceTime)
		if self.numRequests > 1:
			variance = self.intermediateForVariance / (self.numRequests - 1)
		else:
			variance = 0
		self.stdServiceTime = math.sqrt(variance)
		self.sim.stdServiceTime = self.stdServiceTime
		self.sim.avgServiceTime = self.averageServiceTime
	
		# Call original onCompleted
		request.onCompleted()

	## Run control loop.
	# Takes as input the dimmers and computes new weights. Also outputs
	# CVS-formatted statistics through the Simulator's output routine.
	def runControlLoop(self):
		if self.algorithm == 'weighted-RR':
			# Nothing to do here
			pass
		elif self.algorithm == 'optimization':
			setpoint = 1
			arrivalRate = float(self.numRequests - self.lastNumRequests) / float(self.controlPeriod)
			#arrivalRate = 20
			# TODO: we have to substitute these vectors (mu and M) 
			# with estimations of their values
			mutmp = matrix(np.zeros((len(self.weights), 1)))
			Mtmp = matrix(np.zeros((len(self.weights), 1)))
			for i in range(0, len(self.weights)):
				mutmp[i] = self.backends[i].serviceTimeN
				Mtmp[i] = self.backends[i].serviceTimeY
			mu = cvxopt.div(1,mutmp)
			M = cvxopt.div(1,Mtmp)
			A = matrix(np.ones((1, len(self.weights)))) # A and b are constraints for the sum of weights to be 1.0
			b = matrix(1.0, (1,1), 'd')
			m, n = A.size
			# intermediate quantities for optimization
			intA = cvxopt.mul(M,mu)*setpoint - M
			intB = M*arrivalRate*setpoint
			intC = mu - M
			intD = (mu - M)*arrivalRate*setpoint 
			# inequality constraints
			G = matrix(0.0, (3*len(self.weights), len(self.weights)), 'd')
			for i in range(0, len(self.weights)):
				G[i,i] = -1.0 # constraints for nonnegativity of weights
				G[len(self.weights) + i, i] = 1.0 # constrain that lower bound on optimal dimmers is 0
				G[2*len(self.weights) + i, i] = -1.0 # constrain that upper bound on optimal dimmers is 1
			h = matrix(0.0, (3*len(self.weights), 1), 'd')
			for i in range(0, len(self.weights)):
				if intB[i] == 0: # avoid initial corner case
					h[len(self.weights) + i, 0] = 1
					h[2*len(self.weights) + i, 0] = 1
				else:
					h[len(self.weights) + i, 0] = intA[i] / intB[i] # for dimmers greater than 0
					h[2*len(self.weights) + i, 0] = (intC[i] - intA[i]) / (intD[i] + intB[i]) # for dimmers lower than 1
			def F(x=None, z=None):
				if x is None: return 0, matrix(1.0, (n, 1))
				if min(x) <= 0.0: return None
				# function that we want to minimize
				f = -sum(cvxopt.mul(x, cvxopt.div(intA-cvxopt.mul(intB,x), intC+cvxopt.mul(intD,x))))
				Df = -(cvxopt.div((cvxopt.mul(intA,intC) -  \
                                     2*cvxopt.mul(intB,cvxopt.mul(intC,x))-cvxopt.mul(intB,cvxopt.mul(intD,(x**2)))),\
				     ((intC+cvxopt.mul(intD,x))**2))).T
				if z is None: return f, Df
				H = spdiag((
					cvxopt.div(2*cvxopt.mul(intA,cvxopt.mul(intC,intD)), (intC+cvxopt.mul(intD,x))**3) + \
					cvxopt.div(2*cvxopt.mul(intB,(intC**2)), (intC+cvxopt.mul(intD,x))**3)
					))
				return f, Df, H
			#print(-h[2*len(self.weights):3*len(self.weights)])
			lower_tmp = [i for i in -h[2*len(self.weights):3*len(self.weights)] if i > 0]
			lower = sum(lower_tmp)
			#print(lower)
			if lower < 1.0: # if lower > 1 the servers are underloaded!
				#print(self.sim.now, arrivalRate)
				solution = solvers.cp(F, G, h, A=A, b=b)['x']
				self.weights = list(solution)
				#print(self.weights)
			else:
				rest = 1.0
				weights_tmp = matrix(0.0, (len(self.weights),1),'d')
				for i in range(0, len(self.weights)):
					if -h[2*len(self.weights)+i] < rest:
						weights_tmp[i,0] = -h[2*len(self.weights)+i]
						rest = rest + h[2*len(self.weights)+i]
						#print(rest)
					else:
						weights_tmp[i,0] = rest
						break
				#print(weights_tmp)
				self.weights = list(weights_tmp)
				#print(self.weights)		
			x = matrix(self.weights)
			self.sim.output('optimizer', ','.join(map(str, [ self.sim.now ] + \
				list(cvxopt.div(intA-cvxopt.mul(intB,x), intC+cvxopt.mul(intD,x))))))
		elif self.algorithm == 'theta-diff':
			modifiedLastLastThetas = self.lastLastThetas # used to do the quick fix later
			# (by Martina:) a quick and dirty fix for this behavior that when the dimmer
			# is kept to 1 we are not doing a good job
			for i in range(0,len(self.lastThetas)):
				if (self.lastThetas[i] == 1 and self.lastLastThetas[i] == 1):
					modifiedLastLastThetas[i] = 0.99
			# end of the quick fix
			gain = 0.25
			self.weights = [ max(x[0] + gain*(x[1] - x[2]), 0.01) for x in \
				zip(self.weights, self.lastThetas, modifiedLastLastThetas) ]
			preNormalizedSumOfWeights = sum(self.weights)
			self.weights = [ x / preNormalizedSumOfWeights for x in self.weights ]
		elif self.algorithm == 'theta-diff-plus': 
			Kp = 0.5
			Ti = 5.0 
			self.weights = [ max(x[0] * (1 + Kp * (x[1] - x[2]) + (Kp/Ti) * x[1]), 0.01) for x in \
                            zip(self.weights, self.lastThetas, self.lastLastThetas) ]
			preNormalizedSumOfWeights = sum(self.weights)
			self.weights = [ x / preNormalizedSumOfWeights for x in self.weights ]
		elif self.algorithm == 'random':
			# random is not dynamic
			pass
		elif self.algorithm == 'SQF':
			# shortest queue first is not dynamic
			pass
		elif self.algorithm == 'SQF-plus':
			# shortest queue first is not dynamic
			pass
		elif self.algorithm == 'RR':
			# round robin is not dynamic
			pass
		elif self.algorithm == '2RC':
			# two random choices is not dynamic
			pass
		elif self.algorithm == 'FRF':
			# fastest replica first is not dynamic
			pass
		elif self.algorithm == 'FRF-EWMA':
			# slowly forget response times
			ewmaAlpha = 2 / (self.ewmaNumSamples + 1)
			for i in range(0, len(self.backends)):
				self.ewmaResponseTime[i] *= (1 - ewmaAlpha)
		elif self.algorithm == 'predictive':
			# preditctive is not dynamic
			pass
		elif self.algorithm == 'equal-thetas':
			for i in range(0,len(self.backends)):
				# This code was meant to adjust the gain so that the weights of weak servers
				# react faster, since their response times react faster to changing loads.
				# Doesn't work... Yet.
				#theta = self.lastThetas[i]
				#muY = self.backends[i].serviceTimeY
				#muN = self.backends[i].serviceTimeN
				#mueff = 1/(theta/muY + (1-theta)/muN)
				#gamma = 6/mueff
				
				# Gain
				gamma = self.equal_theta_gain
				
				# Calculate the negative deviation from the average
				e = self.lastThetas[i] - avg(self.lastThetas)
				# Integrate the negative deviation from the average
				self.weights[i] += gamma * e # + Kp * (e - self.lastThetaErrors[i])
				self.lastThetaErrors[i] = e

				# Bound
				if self.weights[i] < 0.01:
					self.weights[i] = 0.01
			
			# Normalize
			weightSum = sum(self.weights)
			for i in range(0,len(self.backends)):
				self.weights[i] = self.weights[i] / weightSum
		elif self.algorithm == 'ctl-simplify':
			p = 0.99
			rlsForgetting = 0.99
			# RLS for alpha
			a = [ x[0]*x[1] \
				  for x in zip(self.ctlRlsP,self.weights) ]
			g = [ 1 / (x[0]*x[1] + rlsForgetting) \
			      for x in zip(self.weights,a) ]
			k = [ x[0]*x[1] \
				  for x in zip(g,a)]
			e = [ x[0] - x[1]*x[2]\
				  for x in zip(self.queueLengths,self.weights,self.ctlAlpha)]
			self.ctlAlpha = [ min(x[0] + x[1]*x[2],1.0)\
							  for x in zip(self.ctlAlpha,k,e)]
			self.ctlRlsP  = [ (x[0] - x[1] * x[2]*x[2]) / rlsForgetting \
							  for x in zip(self.ctlRlsP,g,a)]
						
			l = (self.numRequests - self.lastNumRequests) / self.controlPeriod
			xo = -10.0 # desired queue length
			if l == 0:
				for i in range(0,len(self.backends)):
					self.weights[i] = 1/len(self.backends)
			else:
				self.weights = [ max(x[0] + ((1-p)/l)* x[2] * (xo -x[1]) \
						- (1-p)/l* (xo - x[3]), 0.01) for x in \
						zip(self.weights, self.queueLengths, self.ctlAlpha, self.lastQueueLengths) ]
			# Normalize
			for i in range(0,len(self.backends)):
				self.weights[i] = self.weights[i] / sum(self.weights)
		else:
			raise Exception("Unknown load-balancing algorithm " + self.algorithm)

		self.lastNumRequests = self.numRequests
		self.iteration += 1
		self.sim.add(self.controlPeriod, self.runControlLoop)

		# Compute effective weights
		effectiveWeights = [ self.numRequestsPerReplica[i] - self.numLastRequestsPerReplica[i] \
			for i in range(0,len(self.backends)) ]
		effectiveWeights = normalize(effectiveWeights)

		valuesToOutput = [ self.sim.now ] + self.weights + self.lastThetas + \
			[ avg(latencies) for latencies in self.lastLatencies ] + \
			[ max(latencies + [0]) for latencies in self.lastLatencies ] + \
			[ self.numRequests, self.numRequestsWithOptional ] + \
			effectiveWeights
		self.sim.output(self, ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))
		
		self.lastQueueLengths = self.queueLengths
		self.lastLastThetas = self.lastThetas[:]
		self.lastLastLatencies = self.lastLatencies
		self.lastLatencies = [ [] for _ in self.backends ]
		self.numLastRequestsPerReplica = self.numRequestsPerReplica[:]

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

		## Variable that measure the number of requests completed for this user
		# (metric)
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
	# @param _request the request that has been completed (ignored for now)
	def onCompleted(self, _request):
		thinkTime = random.expovariate(1.0 / self.averageThinkTime)
		self.sim.add(thinkTime, self.issueRequest)
		#self.sim.log(self, "Thinking for {0}", thinkTime)
		self.numCompletedRequests += 1

	## Deactive this client.
	# The client will not issue any more requests and no new simulator events
	# are created. Hence, the object can be garbage-collected.
	def deactivate(self):
		self.active = False
	
	## Pretty-print client's name
	def __str__(self):
		return self.name

## Simulates open-loop clients.
# The clients have an exponential arrival time.
class MarkovianArrivalProcess:
	## Constructor.
	# @param sim Simulator to attach client to
	# @param server server-like entity to which requests are sent
	# @param rate average arrival rate
	def __init__(self, sim, server, rate = 1):
		## average arrival rate (model parameter)
		self.rate = rate

		## simulator to which the client is attached
		self.sim = sim
		## server to which requests are issued
		self.server = server

		self.numCompletedRequests = 0
		## Vector of response-times, useful to compute average or distribution (metric)
		self.responseTimes = []

		# Launch arrival process
		self.sim.add(0, lambda: self.issueRequest())

	## Issues a new request to the server.
	def issueRequest(self):
		request = Request()
		request.onCompleted = lambda: self.onCompleted(request)
		self.server.request(request)

		interval = random.expovariate(self.rate)
		self.sim.add(interval, lambda: self.issueRequest())

	## Called when a request completes
	# @param _request the request that has been completed (ignored for now)
	def onCompleted(self, request):
		self.responseTimes.append(self.sim.now - request.arrival)

## Entry-point for simulator.
# Setups up all entities, then runs simulation.
def main():
	algorithms = ("weighted-RR theta-diff optimization SQF SQF-plus FRF equal-thetas " + \
		"FRF-EWMA predictive 2RC RR random theta-diff-plus ctl-simplify").split()

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
	solvers.options['show_progress'] = False # suppress output of cvxopt solver

	random.seed(1)
	sim = Simulator(outputDirectory = args.outdir)
	servers = []
	clients = []
	loadBalancer = LoadBalancer(sim, controlPeriod = 1.0)

	loadBalancer.algorithm = algorithm
	loadBalancer.equal_theta_gain = args.equal_theta_gain
	
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
	
	# For weighted-RR algorithm set the weights
	if algorithm == 'weighted-RR':
		servicetimes = np.array([ x.serviceTimeY for x in servers ])
		sumServiceTimes = sum(servicetimes)
		loadBalancer.weights = list(np.array(servicetimes / sumServiceTimes))


	if 'simulateUntil' not in otherParams:
		raise Exception("Scenario does not define end-of-simulation")
	sim.run(until = otherParams['simulateUntil'])
	recommendationPercentage = float(sim.optionalOn) / float(sim.optionalOff + sim.optionalOn)
	sim.log(sim, loadBalancer.algorithm + \
	    ", total recommendation percentage {0}, standard deviation {1} on mean {2}", \
	    recommendationPercentage, sim.stdServiceTime, sim.avgServiceTime)
	sim.output('final-results', "{algo:15}, {res:.5f}".format(algo = loadBalancer.algorithm, res = recommendationPercentage))

def responseTimeTest():
	results = []
	for i in range(0, 11):
		arrivalRate = 12
		theta = i / 10

		random.seed(1)
		sim = Simulator()
		server = Server(sim, controlPeriod = 0, initialTheta = theta)
		clients = MarkovianArrivalProcess(sim, server, rate = arrivalRate)

		sim.run()

		results.append((theta, avg(clients.responseTimes)))

	print("theta measured modelled")
	for theta, avgResponseTime in results:
		expectedServiceRate = 1 / ((theta * server.serviceTimeY) + (1-theta) * server.serviceTimeN)
		modelledAvgResponseTime = 1 / (expectedServiceRate - arrivalRate)

		print(theta, avgResponseTime, modelledAvgResponseTime)

if __name__ == "__main__":
	main()
	#responseTimeTest()
