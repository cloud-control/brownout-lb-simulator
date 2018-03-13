import numpy as np
import random as xxx_random # prevent accidental usage

from base.utils import *

def getName():
    return 'co-op'

def addCommandLine(parser):
    pass

def parseCommandLine(_args):
    global args
    args = _args

def newInstance(sim, server, name):
    return MMReplicaController(sim, name)

class MMReplicaController:
    def __init__(self, sim, name, seed = 1):
        self.sim = sim
        self.name = name
        ## Control parameters
        self.setpoint = 0.05
        self.error = 0.0
        self.controlPeriod = 0.5
        self.serviceTime = 0.0

        self.latestServiceTimes = []

        ## Random number generator
        self.random = xxx_random.Random()
        self.random.seed(seed)

        if self.controlPeriod > 0:
            self.sim.add(0, self.runControlLoop)


    ## Runs the periodical control loop
    def runControlLoop(self):

        # TODO: Implement service time controller here, do feedback on optional content service times only
        #print "Got to service time controller"

        if not self.latestServiceTimes:
            self.latestServiceTimes.append(0.0)
        valuesToOutput = [ \
            self.sim.now, \
            avg(self.latestServiceTimes),
            ]

        self.sim.output(self, ','.join(["{0:.5f}".format(value) \
            for value in valuesToOutput]))

        self.latestServiceTimes = []
        self.nbrLatestArrivals = 0

        # Re-run later
        self.sim.add(self.controlPeriod, self.runControlLoop)

    def reportData(self, newArrival, responseTime, queueLength, timeY, timeN, optional):
        pass



    def __str__(self):
        return self.name

