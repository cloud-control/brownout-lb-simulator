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

        self.controlPeriod = 0.5

        self.serviceTime = 0.0
        self.filteredServiceTime = 0.0
        self.serviceTimeSetpoint = 0.20
        self.serviceTimeError = 0.0
        self.ctrlActuated = 0

        self.ctrl = 0.0

        self.K = 1.0  # 1.5
        self.Ti = 0.5  # 2.5
        self.beta = 0.6  # 0.6
        self.Tr = 10.0
        self.integralPart = 0.0

        self.latestServiceTimes = []

        ## Random number generator
        self.random = xxx_random.Random()
        self.random.seed(seed)

        if self.controlPeriod > 0:
            self.sim.add(0, self.runControlLoop)


    ## Runs the periodical control loop
    def runControlLoop(self):
        #print "got here 2"
        if self.latestServiceTimes:
            self.filteredServiceTime = 0.5*self.filteredServiceTime + 0.5*avg(self.latestServiceTimes)

        # TODO: Implement service time controller here, do feedback on optional content service times only
        # Service time PI controller

        # Queue length PI controller with reference weighting
        self.serviceTimeError = self.serviceTimeSetpoint - self.filteredServiceTime
        proportionalPart = self.K * (self.beta * self.serviceTimeSetpoint - self.filteredServiceTime)
        prelCtrl = proportionalPart + self.integralPart

        # Saturation: nbr of packets running > 0
        self.ctrl = max(prelCtrl, 0.0)

        # Update controller integral state
        self.updateControllerState(self.ctrl, prelCtrl)


        if not self.latestServiceTimes:
            self.latestServiceTimes.append(0.0)
        valuesToOutput = [ \
            self.sim.now, \
            avg(self.latestServiceTimes),
            self.filteredServiceTime,
            self.serviceTimeSetpoint,
            self.ctrl,
            self.ctrlActuated,
            ]

        self.sim.output(self, ','.join(["{0:.5f}".format(value) \
            for value in valuesToOutput]))

        self.latestServiceTimes = []
        self.nbrLatestArrivals = 0

        # Re-run later
        self.sim.add(self.controlPeriod, self.runControlLoop)

    def updateControllerState(self, ctrl, prelCtrl):
        self.integralPart = self.integralPart + self.serviceTimeError * \
                            (self.K * self.controlPeriod / self.Ti) + \
                            (self.controlPeriod / self.Tr) * (ctrl - prelCtrl)

    def reportData(self, newArrival, responseTime, queueLength, timeY, timeN, optional, serviceTime):
        if optional and not newArrival:
            self.latestServiceTimes.append(serviceTime)

    def decidePacketRequest(self):
        actuationDiff =  int(int(self.ctrl) - self.ctrlActuated)
        self.ctrlActuated = int(self.ctrl)

        packetReq = int(actuationDiff + 1)
        return packetReq

    def __str__(self):
        return self.name

