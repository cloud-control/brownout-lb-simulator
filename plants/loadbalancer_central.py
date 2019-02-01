from __future__ import division

import random as xxx_random # prevent accidental usage
from base import Request


## Simulates a load-balancer with a central queue.
# The load-balancer is assumed to take zero time for its decisions.
class LoadBalancerCentralQueue:
    ## Supported load-balancing algorithms.
    ALGORITHMS = "central-queue".split()

    def __init__(self, sim, seed = 1, printout = 1, printRespTime = 1):
        self.progressPeriod = 1000000.0
        ## what algorithm to use
        self.algorithm = 'central-queue'
        ## Simulator to which the load-balancer is attached
        self.sim = sim
        ## Separate random number generator
        self.random = xxx_random.Random()
        self.random.seed(seed)
        ## list of back-end servers to which requests can be directed
        self.backends = []
        ## queue length of each replica (control input for SQF algorithm)
        self.queueLengths = []
        ## Backends that were removed. They are still tracked to ensure
        # their request queue is properly drained. The keys are the removed
        # backends, whereas the value is an object containing removal-relevant information,
        # currently the number of request to wait for and the callbacks to call when the request
        # queue is drained.
        self.removedBackends = {}

        self.waitingQueue = []

        # Launch progress loop
        self.sim.add(0, self.runProgressLoop)

        self.printout = printout
        self.printRespTime = printRespTime

    ## Adds a new back-end server and initializes decision variables.
    # @param backend the server to add
    def addBackend(self, backend):
        self.backends.append(backend)
        self.queueLengths.append(0)

    ## Remove a backend
    # @param backend backend server to remove
    # @param onCompleted optional callback when backend removal is complete
    def removeBackend(self, backend, onShutdownCompleted = None):
        backendIndex = self.backends.index(backend)
        queueLength = self.queueLengths[backendIndex]
        del self.backends[backendIndex]
        del self.queueLengths[backendIndex]

        if queueLength > 0:
            removedBackendInfo = dict(
                onShutdownCompleted = onShutdownCompleted,
                queueLength = queueLength
            )
            self.removedBackends[backend] = removedBackendInfo
        else:
            if onShutdownCompleted:	onShutdownCompleted()

    def request(self, request):
        if not hasattr(request, 'arrival'):
            request.arrival = self.sim.now
        if not hasattr(request, 'isClone'):
            request.isClone = False

        self.waitingQueue.append(request)
        self.forwardRequest()

    def forwardRequest(self, clonedRequest=None):

        idleIndex = self.getRandomIdleIndex()
        if idleIndex < 0:
            return

        if clonedRequest:
            self.sendRequest(clonedRequest, idleIndex)
        elif len(self.waitingQueue) > 0:
            request = self.waitingQueue.pop(0)
            self.sendRequest(request, idleIndex)

    def sendRequest(self, request, idleIndex):
        request.chosenBackend = self.backends[idleIndex]
        request.chosenBackendIndex = idleIndex
        self.queueLengths[idleIndex] += 1

        if not request.isClone:
            newRequest = Request()
            newRequest.originalRequest = request
            newRequest.requestId = request.requestId

            newRequest.isClone = request.isClone
            newRequest.chosenBackend = request.chosenBackend
            newRequest.chosenBackendIndex = idleIndex
            newRequest.onCompleted = lambda: self.onCompleted(newRequest)
            newRequest.onCanceled = lambda: self.onCanceled(newRequest)
            self.tryCloneRequest(newRequest)
            self.backends[idleIndex].request(newRequest)
        else:
            request.onCompleted = lambda: self.onCompleted(request)
            request.onCanceled = lambda: self.onCanceled(request)
            self.tryCloneRequest(request)
            self.backends[idleIndex].request(request)

    def getRandomIdleIndex(self):
        idleIndexes = [i for i, x in enumerate(self.queueLengths) if (x == 0)]

        if len(idleIndexes) > 0:
            return self.random.choice(idleIndexes)
        else:
            return -1

    def tryCloneRequest(self, request):
        clone = self.sim.cloner.clone(request)

        if clone:
            #self.sim.log(self, "Cloned request " + str(request.requestId))
            self.forwardRequest(clone)

    def onCanceled(self, request):
        #self.sim.log(self, "onCanceled with req id " + str(request.requestId) + "," + str(request.isClone))
        chosenBackendIndex = self.backends.index(request.chosenBackend)
        #self.sim.log(self, "ChosenBackendIndex is " + str(chosenBackendIndex))
        self.queueLengths[chosenBackendIndex] -= 1

    ## Handles request completion.
    # Stores piggybacked dimmer values and calls orginator's onCompleted()
    def onCompleted(self, request):
        #self.sim.log(self, "onCompleted with req id " + str(request.requestId) + "," + str(request.isClone))
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
            #self.sim.log(self, "ChosenBackendIndex is " + str(chosenBackendIndex))

            if self.printRespTime:
                responseTime = request.completion - request.arrival
                # Store response time
                valuesToOutput = [responseTime, chosenBackendIndex]
                self.sim.output(str(self) + '-allReqs', ','.join(["{0:.5f}".format(value) for value in valuesToOutput]))

            self.queueLengths[chosenBackendIndex] -= 1

        request.isCompleted = True
        self.sim.cloner.cancelAllClones(request)

        # Call original onCompleted
        request.originalRequest.onCompleted()

        # Forward new requests to the empty server(s)
        self.forwardRequest()

    def runProgressLoop(self):
        if self.printout:
            print self.sim.now

        self.sim.add(self.progressPeriod, self.runProgressLoop)

    ## Pretty-print load-balancer's name.
    def __str__(self):
        return "lb"

