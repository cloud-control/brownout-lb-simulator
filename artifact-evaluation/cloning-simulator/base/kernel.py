from __future__ import print_function

from collections import defaultdict, deque
import os
import logging
import time
from copy import deepcopy
from base.utils import *

## Simulation kernel.
# Implements an event-driven simulator
class SimulatorKernel:
    ## Constructor
    # @param outputDirectory folder where CSV files should be written to. None disables CSV files
    def __init__(self, cloner=None, outputDirectory = '.', maxRunTime=-1):
        ## events indexed by time
        self.events = defaultdict(list)
        ## reverse index from event handlers to time index, to allow easy update
        self.whatToTime = {}
        ## current simulation time
        self.now = 0.0
        ## cache of open file descriptors: for each issuer, this dictionary maps
        # to a file descriptor
        self.outputFiles = {}
        ## output directory
        self.outputDirectory = outputDirectory
        self.logFile = outputDirectory + '/log.txt'
        self.shouldLog = False

        self.cloner = cloner
        self.servers = None
        self.lastUtilCheck = 0.0
        self.rate = 1.0
        self.utilCheckInterval = 10000.0 / self.rate
        self.maxRunTime = maxRunTime
        self.startTime = time.time()

    def setServers(self, servers):
        self.servers = servers

    def reportRate(self, rate):
        self.rate = rate
        self.utilCheckInterval = 10000.0 / self.rate

    def setupLogging(self, shouldLog):
        self.shouldLog = shouldLog
        if shouldLog:
            logging.basicConfig(filename=self.logFile, level=logging.DEBUG)
            self.logger = logging.getLogger('logger')
            myhandler = logging.FileHandler(self.logFile)
            myhandler.setLevel(logging.DEBUG)
            self.logger.addHandler(myhandler)

    def closeLogging(self):
        if self.shouldLog:
            print("Closing logging!")
            handlers = self.logger.handlers[:]
            for handler in handlers:
                handler.close()
                self.logger.removeHandler(handler)

    ## Adds a new event
    # @param delay non-negative float representing in how much time should the
    # event be triggered. Can be zero, in which case the simulator will trigger
    # the event a bit later, at the current simulation time.
    # @param what Event handler, can be a function, class method or lambda
    # @see Callable
    def add(self, delay, what):
        if what is None:
            print("Added none event at time " + str(self.now))
        self.events[self.now + delay].append(what)
        self.whatToTime[what] = self.now + delay
        return what

    def delete(self, what):
        if what in self.whatToTime:
            oldTime = self.whatToTime[what]
            events = self.events[oldTime]
            events.remove(what)
            if len(events) == 0:
                del self.events[oldTime]
            del self.whatToTime[what]
        #else:
        #    print("Did not find anything to delete!")

    ## Update an existing event or add a new event
    # @param delay in how much time should the event be triggered
    # @param what Callable to call for handling this event. Can be a function,
    # class method or lambda
    # @note Deletes the previously existing event that is handled by what.
    # The current implementation stores at most one such event.
    def update(self, delay, what):
        #print("Got to update in SimKernel")
        self.delete(what)
        self.add(delay, what)

    ## Run the simulation
    # @param until time limit to stop simulation
    def run(self, until = 2000):
        numEvents = 0
        while self.events:
            prevNow = self.now
            self.now = min(self.events)
            #if int(prevNow / 100) < int(self.now / 100):
            #	self.log(self, "progressing, handled {0} events", numEvents)
            events = self.events[self.now]
            #print(str(events))
            event = events.pop(0)
            del self.whatToTime[event]
            if len(events) == 0:
                del self.events[self.now]

            if self.now > until:
                return
            #print("SimKernel: Running new event ")
            #print(str(event))

            if self.isUnstable():
                print("Early termination, system is unstable!")
                print("Completed simulation time: {} of {}".format(self.now, until))
                return

            # Abort if runTime exceeds the predefined roof
            if self.maxRunTime < time.time() - self.startTime and self.maxRunTime > 0:
                print("Early termination, maxRunTime {} limit hit".format(self.maxRunTime))
                print("Completed simulation time: {} of {}".format(self.now, until))
                return

            event()
            numEvents += 1
        self.log(self, "Handled {0} events", numEvents)

    ## Log a simulation message.
    # This function is designed to simplify logging inside the simulator. It
    # prints to standard error
    # the current simulation time, the stringified issuer of the message and the
    # message itself. Includes formatting similar to String.format or
    # Logging.info.
    # @param issuer something that can be rendered as a string through str()
    # @param message the message, first input to String.format
    # @param *args,**kwargs additional arguments to pass to String.format
    def log(self, issuer, message, *args, **kwargs):
        if self.shouldLog:
            self.logger.debug("{0:.6f}, ".format(self.now) + str(issuer)+": " + message.format(*args, **kwargs))

    ## Output simulation data.
    # This function is designed to simplify outputting metrics from a simulated
    # entity. It prints the given line to a file, whose name is derived based on
    # the issuer (currently "sim-{issuer}.csv").
    # @param issuer something that can be rendered as a string through str()
    # @param outputLine the line to output
    # @note outputLine is written verbatimly to the output file, plus a newline
    # is added.
    def output(self, issuer, outputLine):
        if self.outputDirectory == None:
            return
        if issuer not in self.outputFiles:
            outputFilename = 'sim-' + str(issuer) + '.csv'
            outputFilename = os.path.join(self.outputDirectory, outputFilename)
            self.outputFiles[issuer] = open(outputFilename, 'w')
        outputFile = self.outputFiles[issuer]
        outputFile.write(outputLine + "\n")

        # kills performance, but reduces experimenter's impatience :D
        #outputFile.flush()

    def isUnstable(self):
        if (self.now - self.lastUtilCheck) > self.utilCheckInterval:
            utils = []
            for server in self.servers:
                activeTime = deepcopy(server.activeTime)
                if server.isActive:
                    activeTime += (self.now - server.latestActivation)
                util = activeTime / self.now
                utils.append(util)

            meanUtil = avg(utils)
            self.lastUtilCheck = self.now

            return meanUtil > 0.995
        else:
            return False

    ## Pretty-print the simulator kernel's name
    def __str__(self):
        return "kernel"
