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
        self.maxActiveJobs = 1000000
        ## list of request waiting to access server
        self.waitingRequests = []
        ## how often to report metrics
        self.reportPeriod = 1
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
        # Compute utilization
        utilization = (self.getActiveTime() - self.lastActiveTime) / self.reportPeriod

        self.utilization = (self.utilization*self.utilCounter + utilization) / (self.utilCounter + 1)
        self.utilCounter +=1
        #print "util: " + str(self.utilization)

        self.lastActiveTime = self.getActiveTime()

        # Report
        valuesToOutput = [ \
            self.sim.now, \
            avg(self.latestLatencies), \
            maxOrNan(self.latestLatencies), \
            utilization, \
        ]
        self.sim.output(self, ','.join(["{0:.5f}".format(value) \
            for value in valuesToOutput]))

        # Re-run later
        self.latestLatencies = []
        self.sim.add(self.reportPeriod, self.runReportLoop)

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
        # Activate scheduler, if its not active
        if len(self.activeRequests) == 0:
            #print "scheduler was not active at time " + str(self.sim.now) + " in " + str(self)
            self.sim.add(0, self.onScheduleRequests)
        #print "Backend: " + str(request.originalRequest.chosenBackend)
        request.arrival = self.sim.now
        self.controller.reportData(True, 0, 0, 0, 0, 0, 0, request.avgServiceTimeSetpoint)

        # Add request to list of active requests if possible
        if len(self.activeRequests) < self.maxActiveJobs:
            self.activeRequests.append(request)
        else:
            self.waitingRequests.append(request)

        # Report queue length
        valuesToOutput = [ \
            self.sim.now, \
            self.getTotalQueueLength(), \
        ]
        self.sim.output(str(self) + '-arl', ','.join(["{0:.5f}".format(value) \
            for value in valuesToOutput]))

        if self.sim.now > 999.9:
            print "avg run time: " + str(self.avgCancellationTime) + "," + str(request.chosenBackendIndex)
            print "avg util: " + str(self.utilization) + "," + str(request.chosenBackendIndex)

        #print "request() to %s at time %f"%(self.name, self.sim.now)

    def drawServiceTime(self, activeRequest):
        if not hasattr(activeRequest, 'serviceTime'): # 1==1
            #print "Request service time gets set: " + str(activeRequest.requestId)
            meanServiceTime, variance = (self.serviceTimeY, self.serviceTimeYVariance) \
                if activeRequest.withOptional else \
                (self.serviceTimeN, self.serviceTimeNVariance)

            #serviceTime = max(self.random.normalvariate(meanServiceTime, variance), self.minimumServiceTime)
            #serviceTime = np.random.exponential(meanServiceTime)
            serviceTime = np.random.uniform(0.000001, meanServiceTime*2.0)

            activeRequest.serviceTime = serviceTime
            #print "service time set to " + str(serviceTime)
            #self.sim.cloner.setCloneServiceTimes(activeRequest, serviceTime)

            return serviceTime
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

    ## Event handler for scheduling active requests.
    # This function is the core of the processor-sharing with time-slice model.
    # This function is called when "context-switching" occurs. There must be at
    # most one such event registered in the simulation.
    # This function is invoked in the following cases:
    # <ul>
    #   <li>By request(), when the list of active requests was previously empty.
    #   </li>
    #   <li>By onCompleted(), to pick a new request to schedule</li>
    #   <li>By itself, when a request is preempted, i.e., context-switched</li>
    # </ul>
    def onScheduleRequests(self):
        #self.sim.log(self, "scheduling")

        # Measure current queue length first
        currentQueueLength = self.getTotalQueueLength()
        # Select next active request
        activeRequest = self.activeRequests.popleft()
        # Check if this request already is cancelled!
        if self.sim.cloner.isCanceled(activeRequest):
            #print "request is canceled: " + str(activeRequest.requestId) + "," + str(activeRequest.isClone)

            self.printCancellationInfo(activeRequest)

            # Track utilization
            if self.__activeTimeStarted is not None:
                self.__activeTime += self.sim.now - self.__activeTimeStarted
                self.__activeTimeStarted = None

            activeRequest.onCanceled()

            # Append the next request waiting to run (if there is one)
            if (len(self.waitingRequests) > 0) and (len(self.activeRequests) < self.maxActiveJobs):
                waitingRequest = self.waitingRequests.pop(0)
                self.activeRequests.append(waitingRequest)

            # Forget about this request, continue with scheduler
            if len(self.activeRequests) > 0:
                self.sim.add(0, self.onScheduleRequests)
            return

        # Track utilization
        if self.__activeTimeStarted is None:
            self.__activeTimeStarted = self.sim.now

        # Has this request been scheduled before?
        if not hasattr(activeRequest, 'remainingTime'):
            #self.sim.log(self, "request {0} entered the system", activeRequest)

            if not hasattr(activeRequest, 'withOptional'):
                # Pick whether to serve it with optional content or not
                if self.controller:
                    activeRequest.withOptional, activeRequest.theta = self.controller.withOptional(currentQueueLength)
                else:
                    activeRequest.withOptional, activeRequest.theta = True, 1
            #else:
                #print "Opt content decided for request " + str(activeRequest)

            activeRequest.remainingTime = self.drawServiceTime(activeRequest)

        # Schedule it to run for a bit
        timeToExecuteActiveRequest = min(self.timeSlice, activeRequest.remainingTime)
        activeRequest.remainingTime -= timeToExecuteActiveRequest

        # Will it finish?
        if activeRequest.remainingTime == 0:
            # Leave this request in front (onCompleted will pop it)
            self.activeRequests.appendleft(activeRequest)
            # Run onComplete when done
            #print "Req " + str(activeRequest.requestId) + "," + str(activeRequest.isClone) + " completes at " + str(self.sim.now+timeToExecuteActiveRequest)
            self.sim.add(timeToExecuteActiveRequest, lambda: self.onCompleted(activeRequest))
            #self.sim.log(self, "request {0} will execute for {1} to completion", \
            #	activeRequest, timeToExecuteActiveRequest)
        else:
            # Reintroduce it in the active request list at the end for
            # round-robin scheduling
            self.activeRequests.append(activeRequest)

            # Re-run scheduler when time-slice has expired
            self.sim.add(timeToExecuteActiveRequest, self.onScheduleRequests)
            #self.sim.log(self, "request {0} will execute for {1} not to completion",\
            #	activeRequest, timeToExecuteActiveRequest)

    ## Event handler for request completion.
    # Marks the request as completed, calls request.onCompleted() and calls
    # onScheduleRequests() to pick a new request to schedule.
    # @param request request that has received enough service time
    def onCompleted(self, request):
        #print str(self.sim.now) + ": got to onCompleted() for reqId " + str(request.requestId)
        #print request.serviceTime

        # Track utilization
        self.__activeTime += self.sim.now - self.__activeTimeStarted
        self.__activeTimeStarted = None

        # Remove request from active list
        activeRequest = self.activeRequests.popleft()
        if (activeRequest.requestId != request.requestId) or (activeRequest.isClone != request.isClone):
            raise Exception("Weird! Expected request {0},{1} but got {2},{3} instead". \
                    format(request, request.isClone, activeRequest, activeRequest.isClone)) # pragma: no cover

        if not self.sim.cloner.isCanceled(activeRequest):
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

            self.sim.output(str(self)+'-rt', ','.join(["{0:.5f}".format(value) \
                for value in valuesToOutput]))

            # Report queue length
            valuesToOutput = [ \
                self.sim.now, \
                self.getTotalQueueLength(), \
            ]
            self.sim.output(str(self) + '-arl', ','.join(["{0:.5f}".format(value) \
                for value in valuesToOutput]))
        else:
            #print "request is canceled! " + str(activeRequest.requestId) + "," + str(activeRequest.isClone)
            self.printCancellationInfo(activeRequest)
            activeRequest.onCanceled()

        # Append the next request waiting to run (if there is one)
        if (len(self.waitingRequests) > 0) and (len(self.activeRequests) < self.maxActiveJobs):
            waitingRequest = self.waitingRequests.pop(0)
            self.activeRequests.append(waitingRequest)

        # Continue with scheduler
        if len(self.activeRequests) > 0:
            self.sim.add(0, self.onScheduleRequests)

        #if request.isClone:
        #    raise Exception("Clone detected!")


    ## Returns the total queue length (active + waiting requests)
    def getTotalQueueLength(self):
        totalQueue = len(self.activeRequests) + len(self.waitingRequests)
        return totalQueue

    ## Pretty-print server's ID
    def __str__(self):
        return str(self.name)

