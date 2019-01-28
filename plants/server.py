from collections import deque

## Represents a brownout compliant server.
# Current implementation simulates processor-sharing with an infinite number of
# concurrent requests and a fixed time-slice.
class Server:
    ## Variable used for giving IDs to servers for pretty-printing
    lastServerId = 1

    ## Constructor.
    def __init__(self, sim, serviceTimeDistribution=None, seed = 1, ):

        self.serviceTimeDistribution = serviceTimeDistribution

        if self.serviceTimeDistribution is None:
            self.sxModel = True
        else:
            self.sxModel = False

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

        ## Server ID for pretty-printing
        self.name = 'server' + str(Server.lastServerId)
        self.serverId = Server.lastServerId
        Server.lastServerId += 1

        ## Reference to simulator
        self.sim = sim

    def changeMC(self, newMC):
        self.sim.log(self, "In server " + str(self.name) + " with newMC " + str(newMC) + " at " + str(self.sim.now))
        self.maxActiveJobs = newMC

    ## Tells the server to serve a request.
    def request(self, request):
        # self.sim.log(self, "Got to request in server with reqId " + str(request.requestId) + "," + str(request.isClone))

        request.arrival = self.sim.now
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
            request.lastCheckpoint = self.sim.now
            request.processorShare = 1.0/(len(self.activeRequests))
            completionTime = len(self.activeRequests) * request.remainingTime
            self.sim.update(completionTime, request.serverOnCompleted)

    def drawServiceTime(self, activeRequest):
        if not hasattr(activeRequest, 'serviceTime'):
            #self.sim.log(self, "Request service time gets set: " + str(activeRequest.requestId))

            if self.sxModel:
                self.sim.cloner.setCloneServiceTimes(activeRequest)
            else:
                activeRequest.serviceTime = float(self.serviceTimeDistribution.rvs())

            return activeRequest.serviceTime
        else:
            #self.sim.log(self, "Request service time already set: " + str(activeRequest.requestId))
            return activeRequest.serviceTime

    def onCanceled(self, request):
        #self.sim.log(self, "Got to onCanceled for req " + str(request.requestId) + " in server " + str(self))

        activeRequestCanceled = True

        if request in self.activeRequests:
            self.sim.delete(request.serverOnCompleted)
            self.activeRequests.remove(request)
        else:
            self.waitingRequests.remove(request)
            activeRequestCanceled = False

        self.continueWithRequests(activeRequestCanceled)

        request.onCanceled()
        #self.sim.log(self, "Leaving onCanceled() at " + str(self.sim.now))


    ## Event handler for request completion.
    # Marks the request as completed, calls request.onCompleted() and picks a new request to schedule.
    # @param request request that has received enough service time
    def onCompleted(self, request):
        #self.sim.log(self, "Got to onCompleted() for reqId " + str(request.requestId) +  " in " + str(self))

        # Remove request from active list
        self.activeRequests.remove(request)

        if not self.sim.cloner.isCanceled(request):
            #self.sim.log(self, "request is not canceled! " + str(request.requestId) + "," + str(request.isClone))

            # And completed it
            request.completion = self.sim.now
            request.onCompleted()

        else:
            #self.sim.log(self, "request is canceled! " + str(request.requestId) + "," + str(request.isClone))
            request.onCanceled()

        self.continueWithRequests(True)
        #self.sim.log(self, "Done with onCompleted()")

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

