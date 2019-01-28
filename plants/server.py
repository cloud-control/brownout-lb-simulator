from collections import defaultdict, deque
import random as xxx_random # prevent accidental usage
import numpy as np
import scipy.stats

from base.utils import *

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
        ## how often to report metrics
        self.reportPeriod = 500
        ## latencies during the last report interval
        self.latestLatencies = []

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
        # Compute utilization

        alpha = 0.95

        utilization = (self.getActiveTime() - self.lastActiveTime) / self.reportPeriod

        self.utilization = alpha*self.utilization + (1-alpha)*utilization
        #self.sim.log(self, "util: " + str(self.utilization))

        self.lastActiveTime = self.getActiveTime()

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
        #self.sim.log(self, "Got to start running request " + str(request.requestId) + "," + str(request.isClone))
        self.activeRequests.append(request)

        # Track utilization
        if self.__activeTimeStarted is None:
            self.__activeTimeStarted = self.sim.now

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
        #self.sim.log(self, "Got to request in server with reqId " + str(request.requestId) + "," + str(request.isClone))

        request.arrival = self.sim.now
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

    def drawServiceTime(self, activeRequest):
        if not hasattr(activeRequest, 'serviceTime'):
            #self.sim.log(self, "Request service time gets set: " + str(activeRequest.requestId))

            if self.sxModel:
                self.sim.cloner.setCloneServiceTimes(activeRequest)
            else:
                activeRequest.serviceTime = self.serviceTimeDistribution.rvs(1)

            return activeRequest.serviceTime
        else:
            #self.sim.log(self, "Request service time already set: " + str(activeRequest.requestId))
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
        #self.sim.log(self, "Got to onCanceled for req " + str(request.requestId) + " in server " + str(self))
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
        #self.sim.log(self, "Leaving onCanceled() at " + str(self.sim.now))


    ## Event handler for request completion.
    # Marks the request as completed, calls request.onCompleted() and picks a new request to schedule.
    # @param request request that has received enough service time
    def onCompleted(self, request):
        #self.sim.log(self, "Got to onCompleted() for reqId " + str(request.requestId) +  " in " + str(self))
        #self.sim.log(self, "active Reqs: " + str(self.activeRequests))

        # Remove request from active list
        self.activeRequests.remove(request)

        if not self.sim.cloner.isCanceled(request):
            #self.sim.log(self, "request is not canceled! " + str(request.requestId) + "," + str(request.isClone))

            # And completed it
            request.completion = self.sim.now
            self.latestLatencies.append(request.completion - request.arrival)

            request.onCompleted()

            # Report
            valuesToOutput = [ \
                self.sim.now, \
                request.arrival, \
                request.completion - request.arrival, \
            ]

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
            #self.sim.log(self, "request is canceled! " + str(request.requestId) + "," + str(request.isClone))
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
        #self.sim.log(self, "Done with onCompleted()")

    ## Returns the total queue length (active + waiting requests)
    def getTotalQueueLength(self):
        totalQueue = len(self.activeRequests) + len(self.waitingRequests)
        return totalQueue

    ## Pretty-print server's ID
    def __str__(self):
        return str(self.name)

