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
    ALGORITHMS = ("weighted-RR theta-diff SQF SQF-plus FRF equal-thetas equal-queues equal-thetas-SQF clone-SQF " + \
        "FRF-EWMA predictive 2RC RR random fake-random theta-diff-plus ctl-simplify equal-thetas-fast theta-diff-plus-SQF " + \
        "theta-diff-plus-fast SRTF equal-thetas-fast-mul co-op clone-random extremum-clone-random RIQ-d central-queue").split()

    ## Constructor.
    # @param sim Simulator to attach to
    # @param controlPeriod control period
    # @param initialTheta initial dimmer value to consider before receiving any
    # replies from a server
    def __init__(self, sim, controlPeriod = 1, initialTheta = 0.5, seed = 1, nbrClones = 1, printout = 1):
        ## control period (control parameter)
        #self.controlPeriod = controlPeriod # second
        self.controlPeriod = 2.0
        ## initial value of measured theta (control initialization parameter)
        self.initialTheta = initialTheta
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
        ## queue length offset for equal-thetas-SQF
        self.queueOffsets = []
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
        self.latestOptionalLatencies = []
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

        # extremum parameters
        self.feedback = 0.0
        self.high_pass = 0.0
        self.prevFeedback = 0.0
        self.perturbed_high_pass = 0.0
        self.gradient = 0.0
        self.theta_hat = 1.0

        # suppress output of cvxopt solver
        #solvers.options['show_progress'] = False

        # Launch control loop
        self.sim.add(0, self.runControlLoop)

        self.printout = printout

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
            self.lastThetaErrors.append(0)
            self.lastThetas.append(self.initialTheta)
            self.lastLastThetas.append(self.initialTheta)
            self.lastLatencies.append([])
            self.lastQueueLengths.append(0)
            self.queueOffsets.append(0)
            self.numRequestsPerReplica.append(0)
            self.numLastRequestsPerReplica.append(0)
            self.ewmaResponseTime.append(0)
            self.ctlRlsP.append(1000)
            self.ctlAlpha.append(1)
            self.backend_requests.append(0)
        else:
            del self.lastThetaErrors[-1]
            del self.lastThetas[-1]
            del self.lastLastThetas[-1]
            del self.lastLatencies[-1]
            del self.lastQueueLengths[-1]
            del self.queueOffsets[-1]
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
        #print "Got to LB request"
        #self.sim.log(self, "Got request {0}", request)
        if not hasattr(request, 'arrival'):
            request.arrival = self.sim.now
        if not hasattr(request, 'isClone'):
            request.isClone = False
        if self.algorithm in [ 'weighted-RR', 'theta-diff', 'theta-diff-plus', 'equal-thetas', 'ctl-simplify', 'equal-queues' ]:
            chosenBackendIndex = \
                weightedChoice(zip(range(0, len(self.backends)), self.weights), self.random)
        elif self.algorithm == 'equal-thetas-SQF' or self.algorithm == 'equal-thetas-fast' or self.algorithm == 'equal-thetas-fast-mul':
            # Update controller in the -fast version
            if self.algorithm == 'equal-thetas-fast' or self.algorithm == 'equal-thetas-fast-mul':
                dt = self.sim.now - self.lastDecision
                if dt > 1: dt = 1
                for i in range(0,len(self.backends)):
                    # Gain
                    gamma = self.equal_thetas_fast_gain * dt

                    # Calculate the negative deviation from the average
                    e = self.lastThetas[i] - avg(self.lastThetas)
                    # Integrate the negative deviation from the average
                    self.queueOffsets[i] += gamma * e # + Kp * (e - self.lastThetaErrors[i])
                    self.lastThetaErrors[i] = e
                self.lastDecision = self.sim.now

            # To prevent starvation, choose a random empty server..
            empty_servers = [i for i in range(0, len(self.queueLengths)) \
                if self.queueLengths[i] == 0]

            if empty_servers:
                chosenBackendIndex = self.random.choice(empty_servers)
            else:
                if self.algorithm == 'equal-thetas-fast-mul':
                    # ...or choose replica with shortest (queue * 2 ** queueOffset)
                    chosenBackendIndex = \
                        min(range(0, len(self.queueLengths)), \
                        key = lambda i: self.queueLengths[i] * (2 ** (-self.queueOffsets[i])))
                else:
                    # ...or choose replica with shortest (queue + queueOffset)
                    chosenBackendIndex = \
                        min(range(0, len(self.queueLengths)), \
                        key = lambda i: self.queueLengths[i]-self.queueOffsets[i])

        elif self.algorithm == 'theta-diff-plus-SQF':
            # choose replica with shortest (queue + queueOffset)
            chosenBackendIndex = \
                min(range(0, len(self.queueLengths)), \
                key = lambda i: self.queueLengths[i]-self.queueOffsets[i])
            pass
        elif self.algorithm == 'random':
            # round robin
            chosenBackendIndex = \
                self.random.choice(range(0, len(self.backends)))
        elif self.algorithm == 'fake-random':
            #weighters = [0.2, 0.3, 0.5]
            if self.reqNbr > 49:
                self.backend_requests = [0] * len(self.backends)
                self.reqNbr = 0
            else:
                self.reqNbr += 1

            total_reqs = sum(self.backend_requests)
            if total_reqs > 0:
                actual_ratio = [x / total_reqs for x in self.backend_requests]
            else:
                actual_ratio = [0.0] * len(self.backends)
            ratio_diff = [i - j for i, j in zip(self.weights, actual_ratio)]

            """print "req nbr: " + str(self.reqNbr)
            print "backend reqs: " + str(self.backend_requests)
            print "weights: " + str(self.weights)
            print "actual ratio " + str(actual_ratio)
            print "ratio diff: " + str(ratio_diff)"""

            chosenBackendIndex = max(range(0, len(ratio_diff)), key=lambda k: ratio_diff[k])
            self.backend_requests[chosenBackendIndex] += 1

        elif self.algorithm == 'RR':
            # round robin

            chosenBackendIndex = self.reqNbr % len(self.backends)
            self.backend_requests[chosenBackendIndex] += 1

            """print "self.reqNbr: " + str(self.reqNbr)
            print chosenBackendIndex
            print "backend reqs: " + str(self.backend_requests)"""

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

        elif self.algorithm == 'SQF-plus':
            # choose replica with shortest queue
            minIndices = [i for i, x in enumerate(self.queueLengths) if x == min(self.queueLengths)]
            if len(minIndices) == 1:
                chosenBackendIndex = minIndices[0]
            else:
                dimmers = [self.lastThetas[i] for i in minIndices]
                maxDimmerIndex = dimmers.index(max(dimmers))
                chosenBackendIndex = minIndices[maxDimmerIndex]
        elif self.algorithm == '2RC':
            maxlat = [max(x) if x else 0 for x in self.lastLatencies]
            if len(self.backends) == 1:
                chosenBackendIndex = 0
            # randomly select two backends and send it to the one with lowest latency
            else:
                backends = set(range(0, len(self.backends)))
                randomlychosen = self.random.sample(backends, 2)
                if maxlat[randomlychosen[0]] > maxlat[randomlychosen[1]]:
                    chosenBackendIndex = randomlychosen[1]
                else:
                    chosenBackendIndex = randomlychosen[0]
        elif self.algorithm == 'FRF':
            # choose replica with minimum latency
            maxlat = [max(x) if x else 0 for x in self.lastLatencies]
            chosenBackendIndex = \
                maxlat.index(min(maxlat))
        elif self.algorithm == 'FRF-EWMA':
            # choose replica with minimum EWMA latency
            #self.sim.log(self, "EWMA RT {0}", self.ewmaResponseTime)
            chosenBackendIndex = \
                min(range(0, len(self.backends)), \
                key = lambda i: self.ewmaResponseTime[i])
        elif self.algorithm == 'predictive':
            maxlat = np.array([max(x) if x else 0 for x in self.lastLatencies])
            maxlatLast = np.array([max(x) if x else 0 for x in self.lastLastLatencies])
            wlat = 0.2
            wqueue = 0.8
            points = wlat*(maxlat - maxlatLast) + wqueue*(np.array(self.queueLengths) - np.array(self.lastQueueLengths))
            # choose replica with shortest queue
            chosenBackendIndex = \
                min(range(0, len(points)), \
                key = lambda i: points[i])
        elif self.algorithm == "SRTF":
            # choose replica with shortest "time" queue
            #chosenBackendIndex = \
            #	min(range(0, len(self.backends)), \
            #	key = lambda i: sum([r.remainingTime if hasattr(r, 'remainingTime') else 0 for r in self.backends[i].activeRequests]))
            chosenBackendIndex = \
                min(range(0, len(self.queueLengths)), \
                key = lambda i: self.queueLengths[i] * (self.backends[i].serviceTimeY * self.lastThetas[i] + self.backends[i].serviceTimeN * (1 - self.lastThetas[i])))
        elif self.algorithm == 'theta-diff-plus-fast':
            dt = self.sim.now - self.lastDecision
            if dt > 1: dt = 1

            for i in range(0,len(self.backends)):
                # Gain
                Kp = 0.25
                Ti = 5.0
                gammaTr = .01

                # PI control law
                e = self.lastThetas[i] - self.lastLastThetas[i]
                self.queueOffsets[i] += (Kp * e + (Kp/Ti) * self.lastThetas[i]) * dt

                # Anti-windup
                self.queueOffsets[i] -= gammaTr * (self.queueOffsets[i] - self.queueLengths[i]) * dt
                self.lastThetaErrors[i] = e

            self.lastDecision = self.sim.now

            # choose replica with shortest (queue + queueOffset)
            chosenBackendIndex = \
                min(range(0, len(self.queueLengths)), \
                key = lambda i: self.queueLengths[i]-self.queueOffsets[i])

        else:
            raise Exception("Unknown load-balancing algorithm " + self.algorithm)

        if chosenBackendIndex < 0:
            # No server chosen, return
            return

        request.queueDeparture = self.sim.now
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
            newRequest.queueDeparture = request.queueDeparture
            newRequest.avgServiceTimeSetpoint = 0.0
            newRequest.chosenBackend = request.chosenBackend
            newRequest.chosenBackendIndex = chosenBackendIndex
            newRequest.onCompleted = lambda: self.onCompleted(newRequest)
            newRequest.onCanceled = lambda: self.onCanceled(newRequest)
            self.tryCloneRequest(newRequest)
            self.backends[chosenBackendIndex].request(newRequest)
        else:
            request.avgServiceTimeSetpoint = 0.0
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
        if request.withOptional:
            self.numRequestsWithOptional += 1
        #print "got here 5"
        theta = request.theta

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
            self.lastThetas[chosenBackendIndex] = theta
            responseTime = request.completion - request.arrival
            self.lastLatencies[chosenBackendIndex].append(responseTime)
            if request.withOptional:
                self.latestOptionalLatencies.append(responseTime)
                valuesToOutput = [1, responseTime, chosenBackendIndex]
                self.sim.output(str(self) + '-allOpt', ','.join(["{0:.5f}".format(value) for value in valuesToOutput]))
            else:
                valuesToOutput = [0, responseTime, chosenBackendIndex]
                self.sim.output(str(self) + '-allOpt', ','.join(["{0:.5f}".format(value) for value in valuesToOutput]))
            self.queueLengths[chosenBackendIndex] -= 1
            #print "self.queueLengths after" + str(self.queueLengths)
            ewmaAlpha = 2 / (self.ewmaNumSamples + 1)
            self.ewmaResponseTime[chosenBackendIndex] = \
                ewmaAlpha * (request.completion - request.arrival) + \
                (1 - ewmaAlpha) * self.ewmaResponseTime[chosenBackendIndex]

        request.isCompleted = True
        self.sim.cloner.cancelAllClones(request)

        # Call original onCompleted
        request.originalRequest.theta = request.theta
        request.originalRequest.withOptional = request.withOptional
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

        if self.printout:
            self.printProgress()

        if self.algorithm == 'weighted-RR':
            # Nothing to do here
            pass

        elif self.algorithm == 'extremum-clone-random':
            alpha = 0.99
            if self.lastLatencies:
                allLastLatencies = []
                for i in range(0, len(self.backends)):
                    if self.lastLatencies[i]:
                        for j in range(0, len(self.lastLatencies[i])):
                            allLastLatencies.append(self.lastLatencies[i][j])
                allServiced = len(allLastLatencies)
                if allServiced > 2:
                    allLastLatencies.sort()
                    allLastLatencies.pop(0)
                    allLastLatencies.pop(-1)
                    totalRespAvg = sum(allLastLatencies)/ allServiced
                    self.feedback = alpha*self.feedback + (1.0-alpha)*totalRespAvg

            a = 0.3#*self.sim.cloner.nbrClones
            period = 0.062831 * 1.0
            w = period
            wl = period / 3.0
            wh = wl
            k = -0.01

            self.high_pass = (1 - self.controlPeriod * wh) * self.high_pass + self.feedback - self.prevFeedback

            self.perturbed_high_pass = a * math.sin(w * self.sim.now) * self.high_pass

            self.gradient = (1 - self.controlPeriod * wl) * self.gradient + wl * self.perturbed_high_pass

            self.theta_hat = self.theta_hat + k * self.gradient

            self.prevFeedback = self.feedback

            nbrClones = self.theta_hat + a * math.sin(w * self.sim.now)

            # Saturate number of clones
            if nbrClones < 1.0:
                nbrClones = 1.0
                self.theta_hat = nbrClones - a * math.sin(w * self.sim.now)
            elif nbrClones > len(self.backends):
                nbrClones = len(self.backends)
                self.theta_hat = nbrClones - a * math.sin(w * self.sim.now)
            self.sim.cloner.setNbrClones(nbrClones)

            print "feedback: " + str(self.feedback)
            print "gradient: " + str(self.gradient)
            print "optimal nbr: " + str(self.theta_hat)

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
        elif self.algorithm == 'FRF-EWMA':
            # slowly forget response times
            ewmaAlpha = 2 / (self.ewmaNumSamples + 1)
            for i in range(0, len(self.backends)):
                self.ewmaResponseTime[i] *= (1 - ewmaAlpha)
        elif self.algorithm == 'predictive':
            # preditctive is not dynamic
            pass
        elif self.algorithm == 'theta-diff-plus-SQF':
            for i in range(0,len(self.backends)):
                # Gain
                Kp = 0.25
                Ti = 5.0
                gammaTr = .01

                # PI control law
                e = self.lastThetas[i] - self.lastLastThetas[i]
                self.queueOffsets[i] += Kp * e + (Kp/Ti) * self.lastThetas[i]

                # Anti-windup
                self.queueOffsets[i] -= gammaTr * (self.queueOffsets[i] - self.queueLengths[i])
                self.lastThetaErrors[i] = e
        elif self.algorithm == 'equal-thetas-SQF':
            for i in range(0,len(self.backends)):
                # Gain
                gamma = .1
                gammaTr = .01

                # Calculate the negative deviation from the average
                e = self.lastThetas[i] - avg(self.lastThetas)
                # Integrate the negative deviation from the average
                self.queueOffsets[i] += gamma * e # + Kp * (e - self.lastThetaErrors[i])
                self.lastThetaErrors[i] = e
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
        elif self.algorithm == 'equal-queues':
            for i in range(0, len(self.backends)):
                # Gain
                gamma_I = 0.015 # 0.015 gives nice oscillations!
                gamma_P = 0.010

                # Calculate the positive deviation from the average
                e = avg(self.queueLengths) - self.queueLengths[i]
                #print "time: " + str(self.sim.now)
                #print "replica: " + str(i)
                #print "correction term: " + str(gamma*e)

                # Integrate the negative deviation from the average
                self.weights[i] += gamma_I * e + gamma_P*(e - self.lastThetaErrors[i])
                self.lastThetaErrors[i] = e
                #self.weights[i] = gamma_P*e
                #print "weight: " + str(self.weights[i])
                # Bound
                if self.weights[i] < 0.01:
                    self.weights[i] = 0.01

            # Normalize
            weightSum = sum(self.weights)
            for i in range(0, len(self.backends)):
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
                    self.weights[i] = 1.0/len(self.backends)
            else:
                self.weights = [ max(x[0] + ((1-p)/l)* x[2] * (xo -x[1]) \
                        - (1-p)/l* (xo - x[3]), 0.01) for x in \
                        zip(self.weights, self.queueLengths, self.ctlAlpha, self.lastQueueLengths) ]
            # Normalize
            for i in range(0,len(self.backends)):
                self.weights[i] = self.weights[i] / sum(self.weights)
        # Other algorithms are not dynamic

        self.lastNumRequests = self.numRequests
        self.iteration += 1
        self.sim.add(self.controlPeriod, self.runControlLoop)

        # Compute effective weights
        effectiveWeights = [ self.numRequestsPerReplica[i] - self.numLastRequestsPerReplica[i] \
            for i in range(0,len(self.backends)) ]
        effectiveWeights = normalize(effectiveWeights)

        # Output the offsets as weights to enable plotting and stuff
        if self.algorithm == 'equal-thetas-SQF' or self.algorithm == 'equal-thetas-fast' or \
            self.algorithm == 'equal-thetas-fast-mul' or self.algorithm == 'theta-diff-plus-fast' or \
            self.algorithm == 'theta-diff-plus-SQF':
            self.weights = self.queueOffsets

        # Output the offsets as weights to enable plotting and stuff
        if self.algorithm == 'theta-diff-plus-SQF':
            self.weights = self.queueOffsets

        if len(self.latestOptionalLatencies) == 0:
            self.latestOptionalLatencies.append(0.0)

        valuesToOutput = [ self.sim.now ] + [np.percentile(self.latestOptionalLatencies, 95)] + \
                         self.weights + self.lastThetas + \
            [ avg(latencies) for latencies in self.lastLatencies ] + \
            [ max(latencies + [0]) for latencies in self.lastLatencies ] + \
            [ self.numRequests, self.numRequestsWithOptional ] + \
            effectiveWeights
        self.sim.output(self, ','.join(["{0:.5f}".format(value) \
            for value in valuesToOutput]))

        self.lastQueueLengths = self.queueLengths[:]
        self.lastLastThetas = self.lastThetas[:]
        self.lastLastLatencies = self.lastLatencies
        self.latestOptionalLatencies = []
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

