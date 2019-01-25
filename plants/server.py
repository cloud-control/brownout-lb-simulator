from collections import defaultdict, deque
import random as xxx_random # prevent accidental usage
import numpy as np

from base.utils import *

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
    # @note The constructor adds an event into the simulator
    def __init__(self, sim, seed = 1,
            timeSlice = 0.01, \
            serviceTimeY = 0.07, serviceTimeN = 0.001, \
            serviceTimeYVariance = 0.01, serviceTimeNVariance = 0.001, \
            minimumServiceTime = 0.0001):
        ## time slice for scheduling requests (server model parameter)
        #self.timeSlice = timeSlice
        self.timeSlice = 0.0001
        ## service time with optional content (server model parameter)
        self.serviceTimeY = serviceTimeY
        ## service time without optional content (server model parameter)
        self.serviceTimeN = serviceTimeN
        ## service time variance with optional content (server model parameter)
        self.serviceTimeYVariance = serviceTimeYVariance
        #self.serviceTimeYVariance = 0.00000001
        ## service time variance without optional content (server model parameter)
        self.serviceTimeNVariance = serviceTimeNVariance
        #self.serviceTimeNVariance = 0.00000001
        ## minimum service time, despite variance (server model parameter)
        self.minimumServiceTime = minimumServiceTime
        ## list of active requests (server model variable)
        self.activeRequests = deque()
        ## max number of active jobs
        self.maxActiveJobs = 1
        ## list of request waiting to access server
        self.waitingRequests = deque()
        ## how often to report metrics
        self.reportPeriod = 500
        ## latencies during the last report interval
        self.latestLatencies = []
        ## reference to controller
        self.controller = None

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

        ## Random number generator
        self.random = xxx_random.Random()
        self.random.seed(seed)
        #print seed
        np.random.seed(seed)

        self.utilization = 0.0
        self.utilCounter = 0

        self.preCanceled = 0
        self.avgClearRate = 0.0
        self.canceledReqs = 0
        self.avgCancellationTime = 0.0

        # Initialize reporting
        self.runReportLoop()

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

    def changeMC(self, newMC):
        print "In server " + str(self.name) + " with newMC " + str(newMC) + " at " + str(self.sim.now)
        self.maxActiveJobs = newMC

    ## Runs report loop.
    # Regularly report on the status of the server
    def runReportLoop(self):
        #print "Got to report loop"
        # Compute utilization

        alpha = 0.95

        utilization = (self.getActiveTime() - self.lastActiveTime) / self.reportPeriod

        self.utilization = alpha*self.utilization + (1-alpha)*utilization
        #print "util: " + str(self.utilization)

        self.lastActiveTime = self.getActiveTime()

        #print str(self) + ": " + str(self.getTotalQueueLength())

        # Report
        valuesToOutput = [ \
            self.sim.now, \
            avg(self.latestLatencies), \
            maxOrNan(self.latestLatencies), \
            utilization, \
        ]
        #self.sim.output(self, ','.join(["{0:.5f}".format(value) \
        #    for value in valuesToOutput]))

        # Re-run later
        self.latestLatencies = []
        self.sim.add(self.reportPeriod, self.runReportLoop)

    def startRunningRequest(self, request):
        #print "Got to start running request " + str(request.requestId) + "," + str(request.isClone)
        self.activeRequests.append(request)

        # Track utilization
        if self.__activeTimeStarted is None:
            self.__activeTimeStarted = self.sim.now

        request.remainingTime = self.drawServiceTime(request)
        request.lastCheckpoint = self.sim.now
        request.processorShare = 1.0/(len(self.activeRequests))
        #print request.processorShare

        completionTime = len(self.activeRequests)*request.remainingTime

        #print self.sim.now
        #print request.remainingTime
        #print completionTime

        request.serverOnCompleted = lambda: self.onCompleted(request)

        self.sim.add(completionTime, request.serverOnCompleted)

    def updateRunningRequests(self):
        #print "Got to update running requests"
        nbrRequestsActive = len(self.activeRequests)
        for i in range(0, nbrRequestsActive):
            request = self.activeRequests[i]
            #print "old req remainingTime: " + str(request.remainingTime)
            processedTime = (self.sim.now - request.lastCheckpoint)*request.processorShare
            request.remainingTime -= processedTime
            #if processedTime > 0.0:
            #    print "new req remainingTime: " + str(request.remainingTime)
            request.lastCheckpoint = self.sim.now
            request.processorShare = 1.0/(len(self.activeRequests))
            completionTime = len(self.activeRequests) * request.remainingTime
            self.sim.update(completionTime, request.serverOnCompleted)

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
        #print "Got to request in server with reqId " + str(request.requestId) + "," + str(request.isClone)

        request.arrival = self.sim.now
        self.controller.reportData(True, 0, 0, 0, 0, 0, 0, request.avgServiceTimeSetpoint)
        # Start to serve request if possible
        if len(self.activeRequests) < self.maxActiveJobs:
            self.startRunningRequest(request)
            if len(self.activeRequests) > 1:
                self.updateRunningRequests()
        else:
            self.waitingRequests.append(request)
        # Report queue length
        valuesToOutput = [ \
            self.sim.now, \
            self.getTotalQueueLength(), \
        ]
        #self.sim.output(str(self) + '-arl', ','.join(["{0:.5f}".format(value) \
        #    for value in valuesToOutput]))

        #if self.sim.now > 1999.9:
            #print "avg run time: " + str(self.avgCancellationTime) + "," + str(request.chosenBackendIndex)
            #print "avg util: " + str(self.utilization) + "," + str(request.chosenBackendIndex)

        #print "request() to %s at time %f"%(self.name, self.sim.now)

    def drawServiceTime(self, activeRequest):
        activeRequest.withOptional = True
        activeRequest.theta = 1.0
        if not hasattr(activeRequest, 'serviceTime'): # 1==1
            #print "Request service time gets set: " + str(activeRequest.requestId)
            #meanServiceTime, variance = (self.serviceTimeY, self.serviceTimeYVariance) \
            #    if activeRequest.withOptional else \
            #    (self.serviceTimeN, self.serviceTimeNVariance)

            a = self.serviceTimeY
            b = self.serviceTimeN

            #serviceTime = max(self.random.normalvariate(meanServiceTime, variance), self.minimumServiceTime)
            #serviceTime = np.random.exponential(meanServiceTime)
            #serviceTime = self.random.expovariate(1.0/meanServiceTime)
            #serviceTime = self.random.uniform(a, b)
            serviceTime = 0.0
            #print "serviceTime: " + str(serviceTime) + ", " + str(self) + ", req: " + str(activeRequest.requestId)
            #serviceTime = np.random.uniform(0.000001, meanServiceTime*2.0)

            #activeRequest.serviceTime = serviceTime
            #print "service time set to " + str(serviceTime)
            self.sim.cloner.setCloneServiceTimes(activeRequest, serviceTime)
            return activeRequest.serviceTime
        else:
            #print "Request service time already set: " + str(activeRequest.requestId)
            return activeRequest.serviceTime

    def printCancellationInfo(self, activeRequest):
        if not hasattr(activeRequest, 'remainingTime'):
            self.preCanceled += 1
            clearRate = 0.0
            cancellationTime = 0.0
            #runTime =  0.0
            #print str(self.preCanceled) + "," + str(activeRequest.chosenBackendIndex)
        else:
            clearRate = 1 - (activeRequest.remainingTime / activeRequest.serviceTime)
            cancellationTime = (activeRequest.serviceTime - activeRequest.remainingTime)#/activeRequest.serviceTime
            #runTime = self.sim.now - activeRequest.arrival

        self.avgClearRate = (self.canceledReqs * self.avgClearRate + clearRate) / (self.canceledReqs + 1)
        self.avgCancellationTime = (self.canceledReqs * self.avgCancellationTime + cancellationTime) / (self.canceledReqs + 1)
        self.canceledReqs += 1
        # print "chosenbackend: " + str(activeRequest.chosenBackend)
        # print clearRate

        #print str(self.avgClearRate) + "," + str(activeRequest.chosenBackendIndex)
        #if self.sim.now > 199.5:
        #    print "avg cancel: " + str(self.avgCancellationTime) + "," + str(activeRequest.chosenBackendIndex)
        #    print "avg util: " + str(self.utilization) + "," + str(activeRequest.chosenBackendIndex)

        #print str(self.canceledReqs) + "," + str(activeRequest.chosenBackendIndex)

    def onCanceled(self, request):
        #print str(self.sim.now) + ": Got to onCanceled for req " + str(request.requestId) + " in server " + str(self)
        #print self.activeRequests[0].requestId
        self.printCancellationInfo(request)

        activeRequestCanceled = True

        if request in self.activeRequests:
            self.sim.delete(request.serverOnCompleted)
            self.activeRequests.remove(request)
        else:
            self.waitingRequests.remove(request)
            activeRequestCanceled = False

        # Append the next request waiting to run (if there is one)
        if (len(self.waitingRequests) > 0) and (len(self.activeRequests) < self.maxActiveJobs):
            waitingRequest = self.waitingRequests.popleft()
            self.startRunningRequest(waitingRequest)
        elif len(self.activeRequests) > 0:
            if activeRequestCanceled:
                self.updateRunningRequests()
        else:
            # Server has run out of requests, track utilization
            if self.__activeTimeStarted is not None:
                self.__activeTime += self.sim.now - self.__activeTimeStarted
                self.__activeTimeStarted = None

        request.onCanceled()
        #print "Leaving onCanceled() at " + str(self.sim.now)


    ## Event handler for request completion.
    # Marks the request as completed, calls request.onCompleted() and picks a new request to schedule.
    # @param request request that has received enough service time
    def onCompleted(self, request):
        #print str(self.sim.now) + ": got to onCompleted() for reqId " + str(request.requestId) +  " in " + str(self)
        #print request.serviceTime

        #print "active Reqs: " + str(self.activeRequests)

        # Remove request from active list
        self.activeRequests.remove(request)
        #if (activeRequest.requestId != request.requestId) or (activeRequest.isClone != request.isClone):
        #    raise Exception("Weird! Expected request {0},{1} but got {2},{3} instead". \
        #            format(request, request.isClone, activeRequest, activeRequest.isClone)) # pragma: no cover

        if not self.sim.cloner.isCanceled(request):
            #print "request is not canceled! " + str(activeRequest.requestId) + "," + str(activeRequest.isClone)

            # And completed it
            request.completion = self.sim.now
            self.latestLatencies.append(request.completion - request.arrival)
            if self.controller:
                self.controller.reportData(False, request.completion - request.arrival,
                  self.getTotalQueueLength(), self.serviceTimeY, self.serviceTimeN,
                request.withOptional, request.completion - request.queueDeparture, request.avgServiceTimeSetpoint)
                #print "got here 1"
                request.packetRequest = self.controller.decidePacketRequest()
            #print "got here 2"
            request.onCompleted()
            #print "got here 3"

            # Report
            valuesToOutput = [ \
                self.sim.now, \
                request.arrival, \
                request.completion - request.arrival, \
            ]
            #print "got here 4"

            #self.sim.output(str(self)+'-rt', ','.join(["{0:.5f}".format(value) \
            #    for value in valuesToOutput]))

            # Report queue length
            valuesToOutput = [ \
                self.sim.now, \
                self.getTotalQueueLength(), \
            ]
            #self.sim.output(str(self) + '-arl', ','.join(["{0:.5f}".format(value) \
            #    for value in valuesToOutput]))
        else:
            #print "request is canceled! " + str(activeRequest.requestId) + "," + str(activeRequest.isClone)
            self.printCancellationInfo(request)
            request.onCanceled()

        # Append the next request waiting to run (if there is one)
        if (len(self.waitingRequests) > 0) and (len(self.activeRequests) < self.maxActiveJobs):
            waitingRequest = self.waitingRequests.popleft()
            self.startRunningRequest(waitingRequest)
        elif len(self.activeRequests) > 0:
            self.updateRunningRequests()
        else:
            # Server has run out of requests, track utilization
            if self.__activeTimeStarted is not None:
                self.__activeTime += self.sim.now - self.__activeTimeStarted
                self.__activeTimeStarted = None
        #print "Done with onCompleted()"

    ## Returns the total queue length (active + waiting requests)
    def getTotalQueueLength(self):
        totalQueue = len(self.activeRequests) + len(self.waitingRequests)
        return totalQueue

    ## Pretty-print server's ID
    def __str__(self):
        return str(self.name)

