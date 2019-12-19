import random as xxx_random # prevent accidental usage
from collections import deque

## Represents a brownout compliant server.
# Current implementation simulates processor-sharing with an infinite number of
# concurrent requests and a fixed time-slice.
class Server:
    ## Variable used for giving IDs to servers for pretty-printing
    lastServerId = 1

    ## Constructor.
    def __init__(self, sim, serviceTimeDistribution=None, seed = 1, dollySlowdown=1,
                 meanStartupDelay = 0.0, meanCancellationDelay = 0.0):
        self.serviceTimeDistribution = serviceTimeDistribution

        if self.serviceTimeDistribution is None:
            self.sxModel = True
        else:
            self.sxModel = False

        self.dollySlowdown = dollySlowdown

        ## list of active requests (server model variable)
        self.activeRequests = deque()
        ## max number of active jobs
        self.maxActiveJobs = 1
        ## list of request waiting to access server
        self.waitingRequests = deque()

        ## Utilization parameters
        self.activeTime = 0.0
        self.latestActivation = 0.0
        self.isActive = False

        ## Non-perfect parameters
        self.meanStartupDelay = meanStartupDelay
        self.meanCancellationDelay = meanCancellationDelay

        ## Server ID for pretty-printing
        self.name = 'server' + str(Server.lastServerId)
        self.serverId = Server.lastServerId
        seed = seed + 3 + Server.lastServerId
        Server.lastServerId += 1

        ## Separate random number generator
        self.random = xxx_random.Random()
        self.random.seed(seed)

        ## Reference to simulator
        self.sim = sim

    def changeMC(self, newMC):
        self.sim.log(self, "In server " + str(self.name) + " with newMC " + str(newMC) + " at " + str(self.sim.now))
        self.maxActiveJobs = newMC

    ## Tells the server to serve a request.
    def request(self, request):
        # self.sim.log(self, "Got to request in server with reqId " + str(request.requestId) + "," + str(request.isClone))

        request.arrival = self.sim.now

        if self.meanStartupDelay > 0.0:
            startupDelay = self.random.expovariate(1.0/self.meanStartupDelay)
        else:
            startupDelay = 0.0

        request.serverActivateRequest = lambda: self.activateRequest(request)
        self.sim.add(startupDelay, request.serverActivateRequest)

    def activateRequest(self, request):
        # Start to serve request if possible
        if len(self.activeRequests) < self.maxActiveJobs:
            self.startRunningRequest(request)
            if len(self.activeRequests) > 1:
                self.updateRunningRequests()
        else:
            self.waitingRequests.append(request)

    def startRunningRequest(self, request):
        #self.sim.log(self, "Got to start running request " + str(request.requestId) + "," + str(request.isClone))
        self.activeRequests.append(request)

        if not self.isActive:
            self.isActive = True
            self.latestActivation = self.sim.now

        request.remainingTime = self.drawServiceTime(request)
        request.lastCheckpoint = self.sim.now
        request.processorShare = 1.0/(len(self.activeRequests))
        request.avgProcessorShare = 1.0/(len(self.activeRequests))

        completionTime = len(self.activeRequests)*request.remainingTime
        request.serverOnCompleted = lambda: self.onCompleted(request)

        self.sim.add(completionTime, request.serverOnCompleted)

    def updateRunningRequests(self):
        #self.sim.log(self, "Got to update running requests")
        nbrRequestsActive = len(self.activeRequests)

        for i in range(0, nbrRequestsActive):
            request = self.activeRequests[i]
            processedTime = (self.sim.now - request.lastCheckpoint)*request.processorShare
            request.remainingTime -= processedTime

            self.updateAvgProcessorShare(request)
            request.processorShare = 1.0/(len(self.activeRequests))

            request.lastCheckpoint = self.sim.now
            completionTime = len(self.activeRequests) * request.remainingTime
            self.sim.update(completionTime, request.serverOnCompleted)

    def updateAvgProcessorShare(self, request):
        if self.sim.now > request.arrival:
            request.avgProcessorShare = ((request.lastCheckpoint - request.arrival) * request.avgProcessorShare + (
                self.sim.now - request.lastCheckpoint) * request.processorShare) / (self.sim.now - request.arrival)

    def drawServiceTime(self, activeRequest):
        if not hasattr(activeRequest, 'serviceTime'):
            #self.sim.log(self, "Request service time gets set: " + str(activeRequest.requestId))

            if self.sxModel:
                self.sim.cloner.setCloneServiceTimes(activeRequest)
            else:
                #activeRequest.serviceTime = random.expovariate(1.0)
                activeRequest.serviceTime = float(self.serviceTimeDistribution.rvs())

            return activeRequest.serviceTime
        else:
            #self.sim.log(self, "Request service time already set: " + str(activeRequest.requestId))
            return activeRequest.serviceTime

    def onCanceled(self, request):
        #self.sim.log(self, "Got to onCanceled for req " + str(request.requestId) + " in server " + str(self))

        if self.meanCancellationDelay > 0.0:
            cancellationDelay = self.random.expovariate(1.0/self.meanCancellationDelay)
        else:
            cancellationDelay = 0.0

        request.cancellationDelay = cancellationDelay
        request.serverOnCanceled = lambda: self.performCancellation(request)
        self.sim.add(cancellationDelay, request.serverOnCanceled)


    def performCancellation(self, request):

        if request in self.activeRequests:
            self.sim.delete(request.serverOnCompleted)
            self.activeRequests.remove(request)
            self.continueWithRequests(True)

        elif request in self.waitingRequests:
            self.waitingRequests.remove(request)
            self.continueWithRequests(False)

        else:
            self.sim.delete(request.serverActivateRequest)

        request.onCanceled()
        # self.sim.log(self, "Leaving onCanceled() at " + str(self.sim.now))

    ## Event handler for request completion.
    # Marks the request as completed, calls request.onCompleted() and picks a new request to schedule.
    # @param request request that has received enough service time
    def onCompleted(self, request):
        #self.sim.log(self, "Got to onCompleted() for reqId " + str(request.requestId) +  " in " + str(self))

        if not hasattr(request, 'isCanceled'):
            #self.sim.log(self, "request is not canceled! " + str(request.requestId) + "," + str(request.isClone))

            # Remove request from active list
            self.activeRequests.remove(request)

            # And completed it
            request.completion = self.sim.now
            self.updateAvgProcessorShare(request)
            request.onCompleted()

            self.continueWithRequests(True)

        elif hasattr(request, 'cancellationDelay'):
            self.sim.update(0.0, request.serverOnCanceled)


    def continueWithRequests(self, activeRequestStopped):
        # Append the next request waiting to run (if there is one)
        if (len(self.waitingRequests) > 0) and (len(self.activeRequests) < self.maxActiveJobs):
            waitingRequest = self.waitingRequests.popleft()
            self.startRunningRequest(waitingRequest)
        elif len(self.activeRequests) > 0:
            if activeRequestStopped:
                self.updateRunningRequests()
        else:
            # Server has run out of requests, track utilization
            self.activeTime += (self.sim.now - self.latestActivation)
            self.isActive = False

    ## Returns the total queue length (active + waiting requests)
    def getTotalQueueLength(self):
        totalQueue = len(self.activeRequests) + len(self.waitingRequests)
        return totalQueue

    ## Pretty-print server's ID
    def __str__(self):
        return str(self.name)

