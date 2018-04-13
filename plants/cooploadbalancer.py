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
        self.controlPeriod = 0.25

        self.K = 1.5 # 1.5
        self.Ti = 5.0 # 2.5
        self.beta = 1.0 # 0.6
        self.Tr = 10.0

        self.totalKi = 0.0333
        self.totalTr = 10.0

        self.waitingError = 0.0
        self.serviceError = 0.0
        self.responseTimeError = 0.0
        self.totalIntegralPart = 0.0
        self.ratio = 0.9

        self.queueLengthSetpoint = 0.0
        self.avgWaitingTimeSetpoint = 0.0
        self.waitingThreshold = 0.0
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
        self.latestLatenciesPerBackend = []
        self.latestOptionalLatencies = []
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
        self.packetDemands = []
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
        self._resetDecisionVariables(True)

    ## Remove a backend
    # @param backend backend server to remove
    # @param onCompleted optional callback when backend removal is complete
    def removeBackend(self, backend, onShutdownCompleted=None):
        backendIndex = self.backends.index(backend)
        queueLength = self.queueLengths[backendIndex]
        del self.backends[backendIndex]
        del self.queueLengths[backendIndex]
        self._resetDecisionVariables(False)

        if queueLength > 0:
            removedBackendInfo = dict(
                onShutdownCompleted=onShutdownCompleted,
                queueLength=queueLength
            )
            self.removedBackends[backend] = removedBackendInfo
        else:
            if onShutdownCompleted:    onShutdownCompleted()


    ## Reset the decision variables
    def _resetDecisionVariables(self, serverAdded):
        n = len(self.backends)

        if serverAdded:
            self.packetDemands.append(1)
            self.latestLatenciesPerBackend.append([])
            self.lastQueueLengths.append(0)
            self.numRequestsPerReplica.append(0)
            self.numLastRequestsPerReplica.append(0)
            self.ewmaResponseTime.append(0)
            self.ctlRlsP.append(1000)
            self.ctlAlpha.append(1)
            self.backend_requests.append(0)
        else:
            del self.packetDemands[-1]
            del self.latestLatenciesPerBackend[-1]
            del self.lastQueueLengths[-1]
            del self.numRequestsPerReplica[-1]
            del self.numLastRequestsPerReplica[-1]
            del self.ewmaResponseTime[-1]
            del self.ctlRlsP[-1]
            del self.ctlAlpha[-1]
            del self.backend_requests[-1]

        assert len(self.queueLengths) == n

        self.weights = [1.0 / len(self.backends)] * len(self.backends)

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
        packetTemp = deepcopy(self.packetDemands)
        sortedPacketRequests = sorted(enumerate(packetTemp), key=operator.itemgetter(1), reverse=True)

        index, req = sortedPacketRequests[0]
        if req >= 1:
            #print "waiting queue at lb is: " + str(len(self.waitingQueue))
            if self.waitingQueue:
                request = self.waitingQueue.pop(0)
            else:
                return
            request.withOptional, request.theta = self.withOptional(request)
            request.chosenBackend = self.backends[index]
            request.queueDeparture = self.sim.now

            self.packetDemands[index] = self.packetDemands[index] - 1
            waitingTime = request.queueDeparture - request.arrival
            self.latestWaitingTimes.append(waitingTime)

            valuesToOutput = [waitingTime]
            self.sim.output(str(self) + '-tommi', ','.join(["{0:.5f}".format(value) for value in valuesToOutput]))

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

            if max(self.packetDemands) > 0:
                self.sim.add(0, self.forwardRequests)


    ## Inner loop actuator of control signal v deciding execution of optional content
    def withOptional(self, request):

        waitingTime = self.sim.now - request.arrival

        if self.waitingThreshold == 0.0:
            dimmer = 1.0
        elif waitingTime > self.waitingThreshold:
            dimmer = 0.0
        else:
            dimmer = 1.0

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
            responseTime = request.completion - request.arrival
            chosenBackendIndex = self.backends.index(request.chosenBackend)
            self.latestLatenciesPerBackend[chosenBackendIndex].append(responseTime)
            self.latestLatencies.append(responseTime)
            if request.withOptional:
                self.latestServiceTimes.append(request.completion - request.queueDeparture)
                self.latestOptionalLatencies.append(responseTime)
                valuesToOutput = [1, responseTime]
                self.sim.output(str(self) + '-allOpt', ','.join(["{0:.5f}".format(value) for value in valuesToOutput]))
            else:
                valuesToOutput = [0, responseTime]
                self.sim.output(str(self) + '-allOpt', ','.join(["{0:.5f}".format(value) for value in valuesToOutput]))
            self.queueLengths[chosenBackendIndex] -= 1
            #print packetRequest
            self.packetDemands[chosenBackendIndex] += packetRequest
            #print "at onCompleted"
            #print "chosenBackendIndex: " + str(chosenBackendIndex)
            #print str(self.packetDemands)
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

        self.printProgress()

        # Total response time pure I controller on 95th percentile, uses waiting/service time setpoints as actuator
        if self.latestWaitingTimes:
            self.waitingError = self.avgWaitingTimeSetpoint - avg(self.latestWaitingTimes)
        if self.latestServiceTimes:
            self.serviceError = self.avgServiceTimeSetpoint - avg(self.latestServiceTimes)
        if self.latestLatencies:
            self.responseTimeError = self.responseTimeSetpoint - np.percentile(self.latestLatencies, 95)

        # Saturate the I controller on total response times (works as an anti-windup)
        IminResp = -0.5 * self.responseTimeSetpoint
        ImaxResp = 0.0
        self.totalIntegralPart = min(max(self.totalIntegralPart, IminResp), ImaxResp)

        # Total response time controller on the selected statistical measure
        correctedSetpoint = self.responseTimeSetpoint + self.totalIntegralPart

        self.avgWaitingTimeSetpoint = self.ratio * correctedSetpoint
        self.avgServiceTimeSetpoint = (1-self.ratio) * correctedSetpoint

        #self.avgWaitingTimeSetpoint = 0.5
        #self.avgServiceTimeSetpoint = 0.5

        # Saturate the I controller on waiting times (works as an anti-windup)
        IminWait = -0.2 * self.avgWaitingTimeSetpoint
        ImaxWait = 0.2 * self.avgWaitingTimeSetpoint
        self.integralPart = min(max(self.integralPart, IminWait), ImaxWait)

        # Integral controller on avg waiting times using a threshold on request waiting times
        self.waitingThreshold = self.avgWaitingTimeSetpoint + self.integralPart

        # Update total response time controller integral state
        self.updateTotalControllerState()

        # Update waiting time controller integral state
        self.updateControllerState()

        if len(self.latestWaitingTimes) == 0:
            self.latestWaitingTimes.append(0.0)
        if len(self.latestLatenciesPerBackend) == 0:
            self.latestLatenciesPerBackend.append(0.0)
        if len(self.latestServiceTimes) == 0:
            self.latestServiceTimes.append(0.0)
        if len(self.latestOptionalLatencies) == 0:
            self.latestOptionalLatencies.append(0.0)
        if len(self.latestLatencies) == 0:
            self.latestLatencies.append(0.0)

        valuesToOutput = [ self.sim.now ] + [np.percentile(self.latestLatencies, 95)] + \
                         [np.percentile(self.latestOptionalLatencies, 95)] +\
            [ self.numRequests, self.numRequestsWithOptional ] + \
            [avg(self.latestWaitingTimes)] + [np.percentile(self.latestWaitingTimes, 95)] + [len(self.waitingQueue)] + \
            [avg(self.latestServiceTimes) ] + [self.estimatedArrivalRate] + \
            [self.queueLengthSetpoint]  + [self.avgWaitingTimeSetpoint] + \
            [self.avgServiceTimeSetpoint] + [self.waitingThreshold]
        self.sim.output(self, ','.join(["{0:.5f}".format(value) \
            for value in valuesToOutput]))

        self.lastQueueLengths = self.queueLengths[:]
        self.latestLatenciesPerBackend = [ [] for _ in self.backends ]
        self.latestServiceTimes = []
        self.latestWaitingTimes = []
        self.latestOptionalLatencies = []
        self.numLastRequestsPerReplica = self.numRequestsPerReplica[:]
        self.nbrLatestArrivals = 0

        self.lastNumRequests = self.numRequests
        self.iteration += 1
        self.sim.add(self.controlPeriod, self.runControlLoop)

    def updateControllerState(self):
        self.integralPart = self.integralPart + self.waitingError * (self.K * self.controlPeriod / self.Ti)

    def updateTotalControllerState(self):
        self.totalIntegralPart = self.totalIntegralPart + self.responseTimeError * (self.totalKi * self.controlPeriod)

    def printProgress(self):
        modder = int(self.sim.now) % 50
        modder2 = int(self.sim.now * 10) % 10

        if modder == 0 and modder2 == 0:
            print self.sim.now

    ## Pretty-print load-balancer's name.
    def __str__(self):
        return "lb-co-op"