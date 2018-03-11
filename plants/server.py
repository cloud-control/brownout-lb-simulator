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
        self.maxActiveJobs = 3
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

    ## Runs report loop.
    # Regularly report on the status of the server
    def runReportLoop(self):
        # Compute utilization
        utilization = (self.getActiveTime() - self.lastActiveTime) / self.reportPeriod
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
        # Activate scheduler, if its not active
        if len(self.activeRequests) == 0:
            self.sim.add(0, self.onScheduleRequests)

        request.arrival = self.sim.now
        self.controller.reportData(True, 0, 0, 0, 0, 0)

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

        #print "request() to %s at time %f"%(self.name, self.sim.now)

    def drawServiceTime(self, withOptional):
        serviceTime, variance = (self.serviceTimeY, self.serviceTimeYVariance) \
            if withOptional else \
            (self.serviceTimeN, self.serviceTimeNVariance)

        serviceTime = \
            max(self.random.normalvariate(serviceTime, variance), self.minimumServiceTime)

        return serviceTime

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
        # Track utilization
        if self.__activeTimeStarted is None:
            self.__activeTimeStarted = self.sim.now

        # Has this request been scheduled before?
        if not hasattr(activeRequest, 'remainingTime'):
            #self.sim.log(self, "request {0} entered the system", activeRequest)

            # Pick whether to serve it with optional content or not
            if self.controller:
                activeRequest.withOptional, activeRequest.theta = self.controller.withOptional(currentQueueLength)
            else:
                activeRequest.withOptional, activeRequest.theta = True, 1

            activeRequest.remainingTime = self.drawServiceTime(activeRequest.withOptional)

        # Schedule it to run for a bit
        timeToExecuteActiveRequest = min(self.timeSlice, activeRequest.remainingTime)
        activeRequest.remainingTime -= timeToExecuteActiveRequest

        # Will it finish?
        if activeRequest.remainingTime == 0:
            # Leave this request in front (onCompleted will pop it)
            self.activeRequests.appendleft(activeRequest)

            # Run onComplete when done
            self.sim.add(timeToExecuteActiveRequest, \
                lambda: self.onCompleted(activeRequest))
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
        # Track utilization
        self.__activeTime += self.sim.now - self.__activeTimeStarted
        self.__activeTimeStarted = None

        # Remove request from active list
        activeRequest = self.activeRequests.popleft()
        if activeRequest != request:
            raise Exception("Weird! Expected request {0} but got {1} instead". \
                    format(request, activeRequest)) # pragma: no cover

        # And completed it
        request.completion = self.sim.now
        self.latestLatencies.append(request.completion - request.arrival)
        if self.controller:
            self.controller.reportData(False, request.completion - request.arrival,
              self.getTotalQueueLength(), self.serviceTimeY, self.serviceTimeN, request.withOptional)
        request.onCompleted()

        # Append the next request waiting to run (if there is one)
        if len(self.waitingRequests) > 0:
            waitingRequest = self.waitingRequests.pop(0)
            self.activeRequests.append(waitingRequest)

        # Report
        valuesToOutput = [ \
            self.sim.now, \
            request.arrival, \
            request.completion - request.arrival, \
        ]
        self.sim.output(str(self)+'-rt', ','.join(["{0:.5f}".format(value) \
            for value in valuesToOutput]))

        # Report queue length
        valuesToOutput = [ \
            self.sim.now, \
            self.getTotalQueueLength(), \
        ]
        self.sim.output(str(self) + '-arl', ','.join(["{0:.5f}".format(value) \
            for value in valuesToOutput]))

        # Continue with scheduler
        if len(self.activeRequests) > 0:
            self.sim.add(0, self.onScheduleRequests)


    ## Returns the total queue length (active + waiting requests)
    def getTotalQueueLength(self):
        totalQueue = len(self.activeRequests) + len(self.waitingRequests)
        return totalQueue

    ## Pretty-print server's ID
    def __str__(self):
        return str(self.name)

