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
        self.controlPeriod = controlPeriod
        #self.controlPeriod = 0.1

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
        self.queueLengthThreshold = 170
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
        self.packetRequests = [3] * n
        self.latestWaitingTimes = []
        self.latestLatencies = [[] for _ in range(n)]  # to be updated at onComplete
        self.latestServiceTimes = [[] for _ in range(n)]  # to be updated at onComplete
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

        self.waitingQueue.append(request)

        # TODO: Finish this method
        self.forwardRequests()

    def forwardRequests(self):
        # Sort list in descending order
        packetTemp = deepcopy(self.packetRequests)
        sortedPacketRequests = sorted(enumerate(packetTemp), key=operator.itemgetter(1), reverse=True)

        for index, req in sortedPacketRequests:
            for i in range(0, req):
                if self.waitingQueue:
                    request = self.waitingQueue.pop(0)
                else:
                    return
                request.withOptional, request.theta = self.withOptional()
                request.chosenBackend = self.backends[index]
                request.queueDeparture = self.sim.now
                #print "at forwardRequests"
                #print str(self.packetRequests)

                self.packetRequests[index] = self.packetRequests[index] - 1
                self.latestWaitingTimes.append(request.queueDeparture - request.arrival)
                newRequest = Request()
                newRequest.originalRequest = request
                newRequest.withOptional = request.withOptional
                newRequest.theta = request.theta
                #print "forwarding request " + str(newRequest) + " to server " + str(request.chosenBackend)
                newRequest.onCompleted = lambda: self.onCompleted(newRequest)
                # self.sim.log(self, "Directed request to {0}", chosenBackendIndex)
                self.queueLengths[index] += 1
                self.numRequestsPerReplica[index] += 1
                self.backends[index].request(newRequest)

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
                self.latestServiceTimes[chosenBackendIndex]. \
                    append(request.completion - request.queueDeparture)
            self.queueLengths[chosenBackendIndex] -= 1
            self.packetRequests[chosenBackendIndex] += packetRequest
            #print "at onCompleted"
            #print "chosenBackendIndex: " + str(chosenBackendIndex)
            #print str(self.packetRequests)
            ewmaAlpha = 2 / (self.ewmaNumSamples + 1)
            self.ewmaResponseTime[chosenBackendIndex] = \
                ewmaAlpha * (request.completion - request.arrival) + \
                (1 - ewmaAlpha) * self.ewmaResponseTime[chosenBackendIndex]

            self.forwardRequests()

        # Call original onCompleted
        request.onCompleted()

    ## Run control loop.
    # Takes as input the dimmers and computes new weights. Also outputs
    # CVS-formatted statistics through the Simulator's output routine.
    def runControlLoop(self):

        self.lastNumRequests = self.numRequests
        self.iteration += 1
        self.sim.add(self.controlPeriod, self.runControlLoop)

        # TODO: Implement the control strategy (Queue length PI and feedforward for queue length setpoint)


        if len(self.latestWaitingTimes) == 0:
            self.latestWaitingTimes.append(0.0)

        if len(self.latestLatencies) == 0:
            self.latestLatencies.append(0.0)

        if len(self.latestServiceTimes) == 0:
            self.latestLatencies.append(0.0)


        valuesToOutput = [ self.sim.now ] +\
            [ avg(latencies) for latencies in self.latestLatencies ] + \
            [ self.numRequests, self.numRequestsWithOptional ] + \
            [avg(self.latestWaitingTimes)] + \
            [avg(latencies) for latencies in self.latestServiceTimes ]
        self.sim.output(self, ','.join(["{0:.5f}".format(value) \
            for value in valuesToOutput]))

        self.lastQueueLengths = self.queueLengths[:]
        self.latestLatencies = [ [] for _ in self.backends ]
        self.latestServiceTimes = [[] for _ in self.backends]
        self.latestWaitingTimes = []
        self.numLastRequestsPerReplica = self.numRequestsPerReplica[:]

    ## Pretty-print load-balancer's name.
    def __str__(self):
        return "lb-co-op"