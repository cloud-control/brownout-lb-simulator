from __future__ import division

import math
import numpy as np
import random as xxx_random # prevent accidental usage
import operator
from copy import deepcopy

from base import Request
from base.utils import *

## Simulates a co-operative load-balancer.
# The load-balancer is assumed to take zero time for its decisions.
class CoOperativeLoadBalancer:

    def __init__(self, sim, controlPeriod=1, seed=1):
        ## control period (control parameter)
        #self.controlPeriod = controlPeriod
        self.controlPeriod = 0.5

        self.K = 1.5 # 1.5
        self.Ti = 2.5 # 2.5
        self.beta = 0.6 # 0.6
        self.Tr = 10.0

        self.totalKi = 0.0333
        self.totalTr = 10.0

        self.waitingError = 0.0
        self.serviceError = 0.0
        self.responseTimeError = 0.0
        self.totalIntegralPart = 0.0
        self.ratio = 0.8

        self.queueLengthSetpoint = 0.0
        self.avgWaitingTimeSetpoint = 0.0
        self.avgServiceTimeSetpoint = 0.0
        self.responseTimeSetpoint = 1.0
        self.integralPart = 0.0
        self.v = 0.0
        self.queueError = 0.0
        self.feedforward = 0.0

        self.estimatedArrivalRate = 0.0
        self.nbrLatestArrivals = 0

        ## Simulator to which the load-balancer is attached
        self.sim = sim
        ## Separate random number generator
        self.random = xxx_random.Random()
        self.random.seed(seed)
        ## list of back-end servers to which requests can be directed
        self.backends = []
        ## weights determining how to load-balance requests (control output)
        self.weights = []
        ## latencies measured during last control period (metric)
        self.latestLatencies = []
        self.latestOptionalLatencies = []
        ## service times measured during last control period (metric)
        self.latestServiceTimes = []
        ## waiting times measured during last control period
        self.latestWaitingTimes = []
        ## queue length of each replica (control input for SQF algorithm)
        self.queueLengths = []
        self.lastQueueLengths = []
        ## requests waiting in queue at loadbalancer
        self.waitingQueue = []
        ## Packet requests from servers
        self.packetRequests = []
        ## Queue length threshold for waiting queue controller
        self.queueLengthThreshold = 0.0
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
        ## for the ctl-simplify algorithm
        self.ctlRlsP = []
        self.ctlAlpha = []
        ## time when last event-driven control decision was taken
        self.lastDecision = 0
        ## Backends that were removed. They are still tracked to ensure
        # their request queue is properly drained. The keys are the removed
        # backends, whereas the value is an object containing removal-relevant information,
        # currently the number of request to wait for and the callbacks to call when the request
        # queue is drained.
        self.removedBackends = {}

        self.reqNbr = 0
        self.backend_requests = []

        # suppress output of cvxopt solver
        # solvers.options['show_progress'] = False

        # Launch control loop
        self.sim.add(0, self.runControlLoop)

    ## Adds a new back-end server and initializes decision variables.
    # @param backend the server to add
    def addBackend(self, backend):
        self.backends.append(backend)
        self.queueLengths.append(0)
        self._resetDecisionVariables()

    ## Remove a backend
    # @param backend backend server to remove
    # @param onCompleted optional callback when backend removal is complete
    def removeBackend(self, backend, onShutdownCompleted=None):
        backendIndex = self.backends.index(backend)
        queueLength = self.queueLengths[backendIndex]
        del self.backends[backendIndex]
        del self.queueLengths[backendIndex]
        self._resetDecisionVariables()

        if queueLength > 0:
            removedBackendInfo = dict(
                onShutdownCompleted=onShutdownCompleted,
                queueLength=queueLength
            )
            self.removedBackends[backend] = removedBackendInfo
        else:
            if onShutdownCompleted:    onShutdownCompleted()

    ## Reset the decision variables
    def _resetDecisionVariables(self):
        n = len(self.backends)

        # DO NOT USE! `[ [] ] * n` as it leads to undesired behaviour.
        self.waitingQueue = []
        self.packetRequests = [1] * n
        self.latestWaitingTimes = []
        self.latestOptionalLatencies = []
        self.latestLatencies = [[] for _ in range(n)]  # to be updated at onComplete
        self.latestServiceTimes = []  # to be updated at onComplete
        self.lastLastLatencies = [[] for _ in range(n)]
        self.lastQueueLengths = [0] * n
        assert len(self.queueLengths) == n
        self.queueOffsets = [0] * n
        self.numRequestsPerReplica = [0] * n  # to be updated in request
        self.numLastRequestsPerReplica = [0] * n  # to be updated in runControlLoop
        self.ewmaResponseTime = [0] * n  # to be updated in onComplete
        ## for ctl-simplify
        self.ctlRlsP = [1000] * n
        self.ctlAlpha = [1] * n

        self.weights = [1.0 / len(self.backends)] * len(self.backends)
        self.backend_requests = [0] * len(self.backends)
        self.reqNbr = 0


    ## Handles a request.
    # @param request the request to handle
    def request(self, request):
        request.arrival = self.sim.now
        self.nbrLatestArrivals += 1
        self.waitingQueue.append(request)

        # TODO: Finish this method
        self.forwardRequests()

    def forwardRequests(self):
        # Sort list in descending order
        packetTemp = deepcopy(self.packetRequests)
        #print "packet reqs: " + str(packetTemp)
        sortedPacketRequests = sorted(enumerate(packetTemp), key=operator.itemgetter(1), reverse=True)

        index, req = sortedPacketRequests[0]
        if req >= 1:
            #print "waiting queue at lb is: " + str(len(self.waitingQueue))
            if self.waitingQueue:
                request = self.waitingQueue.pop(0)
            else:
                return
            request.withOptional, request.theta = self.withOptional()
            request.chosenBackend = self.backends[index]
            request.queueDeparture = self.sim.now
            #print "at forwardRequests"
            #print str(self.packetRequests)

            #print self.packetRequests[index]

            self.packetRequests[index] = self.packetRequests[index] - 1
            self.latestWaitingTimes.append(request.queueDeparture - request.arrival)
            newRequest = Request()
            newRequest.originalRequest = request
            newRequest.withOptional = request.withOptional
            newRequest.theta = request.theta
            newRequest.queueDeparture = request.queueDeparture
            newRequest.avgServiceTimeSetpoint = self.avgServiceTimeSetpoint
            #print "forwarding request " + str(newRequest) + " to server " + str(request.chosenBackend)
            newRequest.onCompleted = lambda: self.onCompleted(newRequest)
            # self.sim.log(self, "Directed request to {0}", chosenBackendIndex)
            self.queueLengths[index] += 1
            self.numRequestsPerReplica[index] += 1
            self.backends[index].request(newRequest)

            if sum(self.packetRequests) > 0:
                self.sim.add(0, self.forwardRequests)


    ## Inner loop actuator of control signal v deciding execution of optional content
    def withOptional(self):

        # TODO: Implement the estimations?
        #self.saveQueueMeasures(currentQueueLength)

        waitingQueueLength = len(self.waitingQueue)

        # Determine if optional content should be served
        if waitingQueueLength == 1:
            # Always serve optional content if queue is at minimum length
            dimmer = 1.0
        elif waitingQueueLength > self.queueLengthThreshold:
            dimmer = 0.0
        else:
            dimmer = 1.0

        #self.saveDimmerMeasures(dimmer)

        #return self.random.random() <= dimmer, self.expdimmers
        return self.random.random() <= dimmer, 0.5

    ## Handles request completion.
    # Stores piggybacked dimmer values and calls orginator's onCompleted()
    def onCompleted(self, request):
        # "Decapsulate"
        self.numRequests += 1
        if request.withOptional:
            self.numRequestsWithOptional += 1
        theta = request.theta
        packetRequest = request.packetRequest
        request.originalRequest.withOptional = request.withOptional
        request = request.originalRequest
        request.theta = theta

        # Store stats
        request.completion = self.sim.now
        if request.chosenBackend in self.removedBackends:
            removedBackendInfo = self.removedBackends[request.chosenBackend]
            removedBackendInfo['queueLength'] -= 1
            assert removedBackendInfo['queueLength'] >= 0
            if removedBackendInfo['queueLength'] == 0:
                # request queue drained, ready to forget about this backend
                onShutdownCompleted = self.removedBackends[request.chosenBackend]['onShutdownCompleted']
                del self.removedBackends[request.chosenBackend]
                if onShutdownCompleted: onShutdownCompleted()
        else:
            chosenBackendIndex = self.backends.index(request.chosenBackend)
            self.latestLatencies[chosenBackendIndex].\
                append(request.completion - request.arrival)
            if request.withOptional:
                self.latestServiceTimes.append(request.completion - request.queueDeparture)
                self.latestOptionalLatencies.append(request.completion - request.arrival)
            self.queueLengths[chosenBackendIndex] -= 1
            #print packetRequest
            self.packetRequests[chosenBackendIndex] += packetRequest
            #print "at onCompleted"
            #print "chosenBackendIndex: " + str(chosenBackendIndex)
            #print str(self.packetRequests)
            ewmaAlpha = 2 / (self.ewmaNumSamples + 1)
            self.ewmaResponseTime[chosenBackendIndex] = \
                ewmaAlpha * (request.completion - request.arrival) + \
                (1 - ewmaAlpha) * self.ewmaResponseTime[chosenBackendIndex]

            self.sim.add(0, self.forwardRequests)

        # Call original onCompleted
        request.onCompleted()

    ## Run control loop.
    # Takes as input the dimmers and computes new weights. Also outputs
    # CVS-formatted statistics through the Simulator's output routine.
    def runControlLoop(self):

        # Total response time pure I controller on 95th percentile, uses waiting/service time setpoints as actuator
        if self.latestWaitingTimes:
            self.waitingError = self.avgWaitingTimeSetpoint - avg(self.latestWaitingTimes)
        if self.latestServiceTimes:
            self.serviceError = self.avgServiceTimeSetpoint - avg(self.latestServiceTimes)
        if self.latestOptionalLatencies:
            self.responseTimeError = self.responseTimeSetpoint - np.percentile(self.latestOptionalLatencies, 95)

        correctedSetpointPrel = self.responseTimeSetpoint + self.totalIntegralPart

        # Saturation: No setpoints below zero
        correctedSetpoint = max(correctedSetpointPrel, 0.0)

        self.avgWaitingTimeSetpoint = self.ratio * correctedSetpoint
        self.avgServiceTimeSetpoint = (1-self.ratio) * correctedSetpoint

        # Update controller integral state
        self.updateTotalControllerState(correctedSetpoint, correctedSetpointPrel)

        # Estimate current arrival rate
        alpha_a = 0.9
        self.estimatedArrivalRate = (1-alpha_a) * self.estimatedArrivalRate + alpha_a * self.nbrLatestArrivals / self.controlPeriod

        # Feedforward controller on waiting times, determines queue length setpoint
        self.queueLengthSetpoint = self.avgWaitingTimeSetpoint*self.estimatedArrivalRate + 1

        queueLength = len(self.waitingQueue)
        self.queueError = self.queueLengthSetpoint - queueLength

        # Queue length PI controller with reference weighting
        proportionalPart = self.K *(self.beta*self.queueLengthSetpoint - queueLength)
        prelV = proportionalPart + self.integralPart

        # Saturation: No queue length thresholds below zero
        self.v = max(prelV, -1.0 * len(self.waitingQueue))

        # Set threshold for actuation of control signal v
        self.queueLengthThreshold = queueLength + self.v

        # Update controller integral state
        self.updateControllerState(self.v, prelV)

        if len(self.latestWaitingTimes) == 0:
            self.latestWaitingTimes.append(0.0)
        if len(self.latestLatencies) == 0:
            self.latestLatencies.append(0.0)
        if len(self.latestServiceTimes) == 0:
            self.latestServiceTimes.append(0.0)
        if len(self.latestOptionalLatencies) == 0:
            self.latestOptionalLatencies.append(0.0)

        valuesToOutput = [ self.sim.now ] +\
            [ avg(latencies) for latencies in self.latestLatencies ] + \
            [ self.numRequests, self.numRequestsWithOptional ] + \
            [avg(self.latestWaitingTimes)] + [np.percentile(self.latestWaitingTimes, 95)] + [len(self.waitingQueue)] + \
            [avg(self.latestServiceTimes) ] + [self.estimatedArrivalRate] + \
            [self.queueLengthSetpoint] + [np.percentile(self.latestOptionalLatencies, 95)] + [self.avgWaitingTimeSetpoint] + \
            [self.avgServiceTimeSetpoint]
        self.sim.output(self, ','.join(["{0:.5f}".format(value) \
            for value in valuesToOutput]))

        self.lastQueueLengths = self.queueLengths[:]
        self.latestLatencies = [ [] for _ in self.backends ]
        self.latestServiceTimes = []
        self.latestWaitingTimes = []
        self.latestOptionalLatencies = []
        self.numLastRequestsPerReplica = self.numRequestsPerReplica[:]
        self.nbrLatestArrivals = 0

        self.lastNumRequests = self.numRequests
        self.iteration += 1
        self.sim.add(self.controlPeriod, self.runControlLoop)

    def updateControllerState(self, v, prelV):
        self.integralPart = self.integralPart + self.queueError * \
                            (self.K * self.controlPeriod / self.Ti) + \
                            (self.controlPeriod / self.Tr) * (v - prelV)

    def updateTotalControllerState(self, v, prelV):
        self.totalIntegralPart = self.totalIntegralPart + self.responseTimeError * \
                            (self.totalKi * self.controlPeriod) + \
                            (self.controlPeriod / self.totalTr) * (v - prelV)

    ## Pretty-print load-balancer's name.
    def __str__(self):
        return "lb-co-op"