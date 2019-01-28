from __future__ import division

import math
import numpy as np
import random as xxx_random # prevent accidental usage

from base import Request
from base.utils import *

## Simulates a load-balancer.
# The load-balancer is assumed to take zero time for its decisions.
class LoadBalancer:
    ## Supported load-balancing algorithms.
    ALGORITHMS = "SQF clone-SQF random RR clone-random RIQ-d central-queue".split()

    ## Constructor.
    # @param sim Simulator to attach to
    # @param controlPeriod control period
    # @param initialTheta initial dimmer value to consider before receiving any
    # replies from a server
    def __init__(self, sim, seed = 1):
        ## control period (control parameter)
        #self.controlPeriod = controlPeriod # second
        self.controlPeriod = 2.0
        ## what algorithm to use
        self.algorithm = 'theta-diff'

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
        self.lastLatencies = []
        self.lastLastLatencies = []
        ## queue length of each replica (control input for SQF algorithm)
        self.queueLengths = []
        ## number of requests, with or without optional content, served since
        # the load-balancer came online (metric)
        self.numRequests = 0
        self.lastNumRequests = 0
        ## number of requests served by each replica (metric).
        self.numRequestsPerReplica = []
        ## number of requests served by each replica before the last control period (metric).
        self.numLastRequestsPerReplica = []
        self.iteration = 1
        ## Backends that were removed. They are still tracked to ensure
        # their request queue is properly drained. The keys are the removed
        # backends, whereas the value is an object containing removal-relevant information,
        # currently the number of request to wait for and the callbacks to call when the request
        # queue is drained.
        self.removedBackends = {}

        self.reqNbr = 0
        self.backend_requests = []

        self.idleIndexes = []

        self.centralQueue = []

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
    def removeBackend(self, backend, onShutdownCompleted = None):
        backendIndex = self.backends.index(backend)
        queueLength = self.queueLengths[backendIndex]
        del self.backends[backendIndex]
        del self.queueLengths[backendIndex]
        self._resetDecisionVariables(False)

        if queueLength > 0:
            removedBackendInfo = dict(
                onShutdownCompleted = onShutdownCompleted,
                queueLength = queueLength
            )
            self.removedBackends[backend] = removedBackendInfo
        else:
            if onShutdownCompleted:	onShutdownCompleted()

    ## Reset the decision variables
    def _resetDecisionVariables(self, serverAdded):
        n = len(self.backends)

        if serverAdded:
            self.lastLatencies.append([])
            self.lastQueueLengths.append(0)
            self.numRequestsPerReplica.append(0)
            self.numLastRequestsPerReplica.append(0)
            self.backend_requests.append(0)
        else:
            del self.lastLatencies[-1]
            del self.lastQueueLengths[-1]
            del self.numRequestsPerReplica[-1]
            del self.numLastRequestsPerReplica[-1]
            del self.backend_requests[-1]

        assert len(self.queueLengths) == n

    ## Handles a request.
    # @param request the request to handle
    def request(self, request):
        self.sim.log(self, "Got to LB request ffs")
        #self.sim.log(self, "Got request {0}", request)
        if not hasattr(request, 'arrival'):
            request.arrival = self.sim.now
        if not hasattr(request, 'isClone'):
            request.isClone = False

        if self.algorithm == 'random':
            chosenBackendIndex = \
                self.random.choice(range(0, len(self.backends)))

        elif self.algorithm == 'RR':
            # round robin
            chosenBackendIndex = self.reqNbr % len(self.backends)
            self.backend_requests[chosenBackendIndex] += 1

            self.reqNbr += 1

        elif self.algorithm == 'SQF':
            # choose replica with shortest queue, choose randomly between the shortest
            shortestQueue = min(self.queueLengths)
            shortestIndexes = [i for i, x in enumerate(self.queueLengths) if x == shortestQueue]
            chosenBackendIndex = self.random.choice(shortestIndexes)

        elif self.algorithm == 'clone-SQF':
            #print "got to clone sqf LB-method"
            if hasattr(request, 'illegalServers'):
                legalServers = [queue for index, queue in enumerate(self.queueLengths) if index not in request.illegalServers]
                #print legalServers
                shortestQueue = min(legalServers)
                shortestIndexes = [i for i, x in enumerate(self.queueLengths) if (x == shortestQueue) and i not in request.illegalServers]
                #print "Clone with reqid " + str(request.requestId) + " can be sent to " + str(legalServers)
            else:
                shortestQueue = min(self.queueLengths)
                shortestIndexes = [i for i, x in enumerate(self.queueLengths) if (x == shortestQueue)]

            # choose replica with shortest queue, choose randomly between the shortest
            chosenBackendIndex = self.random.choice(shortestIndexes)
            #print self.queueLengths

        elif (self.algorithm == 'clone-random') or (self.algorithm == 'extremum-clone-random'):
            #print "got to clone sqf LB-method"
            if hasattr(request, 'illegalServers'):
                legalIndexes = [index for index, queue in enumerate(self.queueLengths) if index not in request.illegalServers]
                #print "Clone with reqid " + str(request.requestId) + " can be sent to " + str(legalServers)
            else:
                legalIndexes = range(0, len(self.backends))

            # choose random replica among the legal ones
            chosenBackendIndex = self.random.choice(legalIndexes)
            #print request.requestId
            #print chosenBackendIndex
            #print self.queueLengths

        elif self.algorithm == 'central-queue':
            #print self.queueLengths

            idleIndexes = [index for index, queue in enumerate(self.queueLengths) if queue == 0]
            #print self.sim.now
            #print idleIndexes

            if hasattr(request, 'hasWaited') or request.isClone:
                #print len(idleIndexes)
                chosenBackendIndex = self.random.choice(idleIndexes)
                #print str(request.requestId) + "," + str(request.isClone) + " will be sent to " + str(chosenBackendIndex)
            else:
                if (len(self.centralQueue) == 0) and (len(idleIndexes) > 0):
                    # Dispatch the new request immediately
                    chosenBackendIndex = self.random.choice(idleIndexes)
                    #print str(request.requestId) + "," + str(request.isClone) + " will be sent to " + str(chosenBackendIndex)
                    #print idleIndexes
                    #print request.requestId
                    #print chosenBackendIndex
                else:
                    # Do not dispatch now
                    self.centralQueue.append(request)
                    #print len(self.centralQueue)
                    chosenBackendIndex = -1

        elif self.algorithm == 'RIQ-d':
            #print "got to clone sqf LB-method"
            legalIndexes = []
            if not request.isClone:
                # First original request, get idle server indexes
                d = 12
                serverIndexes = self.random.sample(xrange(0, len(self.queueLengths)), d)
                #print serverIndexes
                servers = [(index, queue) for index, queue in enumerate(self.queueLengths) if index in serverIndexes]
                #print servers
                self.idleIndexes = [index for index, queue in servers if queue == 0]
                #print self.idleIndexes
                if len(self.idleIndexes) == 0:
                    self.sim.cloner.setNbrClones(1)
                    legalIndexes = serverIndexes
                else:
                    self.sim.cloner.setNbrClones(len(self.idleIndexes))
                    #self.sim.cloner.setNbrClones(1)
                    legalIndexes = self.idleIndexes
                #print self.idleIndexes
            if hasattr(request, 'illegalServers'):
                legalIndexes = [index for index in self.idleIndexes if index not in request.illegalServers]
                #print legalIndexes
                #print "Clone with reqid " + str(request.requestId) + " can be sent to " + str(legalServers)
            elif request.isClone:
                legalIndexes = self.idleIndexes

            # choose random replica among the legal ones
            chosenBackendIndex = self.random.choice(legalIndexes)
            #print chosenBackendIndex
            #print self.queueLengths

        else:
            raise Exception("Unknown load-balancing algorithm " + self.algorithm)

        if chosenBackendIndex < 0:
            # No server chosen, return
            return

        request.chosenBackend = self.backends[chosenBackendIndex]
        request.chosenBackendIndex = chosenBackendIndex
        self.queueLengths[chosenBackendIndex] += 1
        self.numRequestsPerReplica[chosenBackendIndex] += 1

        #print "Dispatching with req id " + str(request.requestId) + "," + str(request.isClone) + " to " + str(chosenBackendIndex)
        #print "ChosenBackendIndex is " + str(chosenBackendIndex)
        #print "self.queueLengths: " + str(self.queueLengths)
        if not request.isClone:
            newRequest = Request()
            newRequest.originalRequest = request
            newRequest.requestId = request.requestId

            newRequest.isClone = request.isClone
            newRequest.chosenBackend = request.chosenBackend
            newRequest.chosenBackendIndex = chosenBackendIndex
            newRequest.onCompleted = lambda: self.onCompleted(newRequest)
            newRequest.onCanceled = lambda: self.onCanceled(newRequest)
            self.tryCloneRequest(newRequest)
            self.backends[chosenBackendIndex].request(newRequest)
        else:
            request.onCompleted = lambda: self.onCompleted(request)
            request.onCanceled = lambda: self.onCanceled(request)
            self.tryCloneRequest(request)
            self.backends[chosenBackendIndex].request(request)


    def tryCloneRequest(self, request):
        #print "got to tryCloneRequest"

        #print self.sim.now
        #print "Cloning request with id " + str(request.requestId)

        clone = self.sim.cloner.clone(request, self.queueLengths, self.backends)
        # Dispatch the new clone
        if clone:
            #print "Cloned request " + str(request.requestId)
            self.request(clone)


    def onCanceled(self, request):
        #print "LB: onCanceled with req id " + str(request.requestId) + "," + str(request.isClone)
        chosenBackendIndex = self.backends.index(request.chosenBackend)
        #print "ChosenBackendIndex is " + str(chosenBackendIndex)
        #print "self.queueLengths before: " + str(self.queueLengths)
        self.queueLengths[chosenBackendIndex] -= 1
        #print "self.queueLengths after: " + str(self.queueLengths)

    ## Handles request completion.
    # Stores piggybacked dimmer values and calls orginator's onCompleted()
    def onCompleted(self, request):
        #print "LB: onCompleted with req id " + str(request.requestId) + "," + str(request.isClone)

        #print "self.queueLengths before" + str(self.queueLengths)

        #print "In loadbalancers onCompleted()"
        #print "Request: " + str(request.requestId) + "," + str(request.isClone)
        #print "got here 3"

        self.numRequests += 1
        #print "got here 4"
        #print "got here 5"

        #request = request.originalRequest
        #request.theta = theta

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
            #print "ChosenBackendIndex is " + str(chosenBackendIndex)
            responseTime = request.completion - request.arrival
            self.lastLatencies[chosenBackendIndex].append(responseTime)

            # Store response time
            valuesToOutput = [responseTime, chosenBackendIndex]
            self.sim.output(str(self) + '-allReqs', ','.join(["{0:.5f}".format(value) for value in valuesToOutput]))

            self.queueLengths[chosenBackendIndex] -= 1
            #print "self.queueLengths after" + str(self.queueLengths)

        request.isCompleted = True
        self.sim.cloner.cancelAllClones(request)

        # Call original onCompleted
        request.originalRequest.onCompleted()
        #print "LB: OnComplete: " + str(request.requestId) + "," + str(request.isClone)
        #print "LB: OnComplete: " + str(request.remainingTime)

        #print self.algorithm

        if self.algorithm == 'central-queue':
            #print "Got to dispatching next req!"
            #print self.queueLengths
            # Dispatch next waiting request (if it exists)
            if len(self.centralQueue) > 0:
                waitingRequest = self.centralQueue.pop(0)
                waitingRequest.hasWaited = True
                #print "Dispatching waiting req " + str(waitingRequest.requestId)
                self.sim.add(0, lambda: self.request(waitingRequest))

    ## Run control loop.
    # Takes as input the dimmers and computes new weights. Also outputs
    # CVS-formatted statistics through the Simulator's output routine.
    def runControlLoop(self):

        self.printProgress()

        self.lastNumRequests = self.numRequests
        self.iteration += 1
        self.sim.add(self.controlPeriod, self.runControlLoop)

        valuesToOutput = [ self.sim.now ] + \
            [ avg(latencies) for latencies in self.lastLatencies ] + \
            [ max(latencies + [0]) for latencies in self.lastLatencies ] + \
            [ self.numRequests]
        self.sim.output(self, ','.join(["{0:.5f}".format(value) \
            for value in valuesToOutput]))

        self.lastQueueLengths = self.queueLengths[:]
        self.lastLatencies = [ [] for _ in self.backends ]
        self.numLastRequestsPerReplica = self.numRequestsPerReplica[:]

    def printProgress(self):
        modder = int(self.sim.now) % 500
        modder2 = int(self.sim.now * 100) % 100

        if modder == 0 and modder2 == 0:
            print self.sim.now

    ## Pretty-print load-balancer's name.
    def __str__(self):
        return "lb"

