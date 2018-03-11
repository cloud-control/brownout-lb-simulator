from __future__ import division

import math
import numpy as np
import random as xxx_random # prevent accidental usage

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

        self.latestLatencies = [[] for _ in range(n)]  # to be updated at onComplete
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

        # Define which backend to send request to, or queue it!
        chosenBackendIndex = 0

        request.chosenBackend = self.backends[chosenBackendIndex]
        newRequest = Request()
        newRequest.originalRequest = request
        newRequest.onCompleted = lambda: self.onCompleted(newRequest)
        #self.sim.log(self, "Directed request to {0}", chosenBackendIndex)
        self.queueLengths[chosenBackendIndex] += 1
        self.numRequestsPerReplica[chosenBackendIndex] += 1
        self.backends[chosenBackendIndex].request(newRequest)

    ## Handles request completion.
    # Stores piggybacked dimmer values and calls orginator's onCompleted()
    def onCompleted(self, request):
        # "Decapsulate"
        self.numRequests += 1
        if request.withOptional:
            self.numRequestsWithOptional += 1
        theta = request.theta
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
            self.queueLengths[chosenBackendIndex] -= 1
            ewmaAlpha = 2 / (self.ewmaNumSamples + 1)
            self.ewmaResponseTime[chosenBackendIndex] = \
                ewmaAlpha * (request.completion - request.arrival) + \
                (1 - ewmaAlpha) * self.ewmaResponseTime[chosenBackendIndex]

        # Call original onCompleted
        request.onCompleted()

    ## Run control loop.
    # Takes as input the dimmers and computes new weights. Also outputs
    # CVS-formatted statistics through the Simulator's output routine.
    def runControlLoop(self):

        self.lastNumRequests = self.numRequests
        self.iteration += 1
        self.sim.add(self.controlPeriod, self.runControlLoop)

        # Do periodical stuff, e.g. to update queue length setpoint


        valuesToOutput = [ self.sim.now ] + self.weights + self.lastThetas + \
            [ avg(latencies) for latencies in self.lastLatencies ] + \
            [ max(latencies + [0]) for latencies in self.lastLatencies ] + \
            [ self.numRequests, self.numRequestsWithOptional ] + \
            effectiveWeights
        self.sim.output(self, ','.join(["{0:.5f}".format(value) \
            for value in valuesToOutput]))

        self.lastQueueLengths = self.queueLengths[:]
        self.lastLastThetas = self.lastThetas[:]
        self.lastLastLatencies = self.lastLatencies
        self.lastLatencies = [ [] for _ in self.backends ]
        self.numLastRequestsPerReplica = self.numRequestsPerReplica[:]

    ## Pretty-print load-balancer's name.
    def __str__(self):
        return "lb-co-op"