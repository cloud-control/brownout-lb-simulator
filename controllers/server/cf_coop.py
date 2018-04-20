import numpy as np
import random as xxx_random  # prevent accidental usage
import math

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
    def __init__(self, sim, name, seed=1):
        self.sim = sim
        self.name = name
        ## Control parameters

        self.controlPeriod = 0.5

        self.serviceTime = 0.0
        self.filteredServiceTime = 0.0
        self.avgServiceTimeSetpoint = 0.0
        self.serviceTimeError = 0.0
        self.ctrlActuated = 0

        self.ctrl = 0.0

        self.ki = 0.0
        self.integralPart = 0.0
        self.estimatedProcessGain = 0.05

        self.nbrRunningRequests = 0

        self.latestServiceTimes = []

        ## Random number generator
        self.random = xxx_random.Random()
        self.random.seed(seed)

        if self.controlPeriod > 0:
            self.sim.add(0, self.runControlLoop)

    ## Runs the periodical control loop
    def runControlLoop(self):

        # Estimate process gain (relation between nbr of packets being served and the service time)
        alpha_p = 0.5
        if self.latestServiceTimes:
            self.estimatedProcessGain = (1 - alpha_p) * self.estimatedProcessGain + \
                alpha_p * avg(self.latestServiceTimes) / (self.ctrlActuated + 1)

        # Adaptive I controller on unfiltered 95th percentile of service times
        b = 0.8 # Placement of integrator pole
        a = 1.0 - b # Placement of process pole

        self.ki = a*b/self.estimatedProcessGain

        if self.latestServiceTimes:
            self.serviceTimeError = self.avgServiceTimeSetpoint - avg(self.latestServiceTimes)

        Imin = 0.0
        Imax = 5.0 + self.nbrRunningRequests

        self.integralPart = min(max(self.integralPart, Imin), Imax)

        self.ctrl = self.integralPart

        # Update controller integral state
        self.updateIControllerState()

        if not self.latestServiceTimes:
            self.latestServiceTimes.append(0.0)
        valuesToOutput = [
            self.sim.now,
            np.percentile(self.latestServiceTimes, 95),
            self.filteredServiceTime,
            self.avgServiceTimeSetpoint,
            self.ctrl,
            self.ctrlActuated+1,
            self.estimatedProcessGain,
        ]

        self.sim.output(self, ','.join(["{0:.5f}".format(value) \
                                        for value in valuesToOutput]))

        self.latestServiceTimes = []
        self.nbrLatestArrivals = 0

        # Re-run later
        self.sim.add(self.controlPeriod, self.runControlLoop)

    def updateIControllerState(self):
        self.integralPart = self.integralPart + self.serviceTimeError * self.ki

    def reportData(self, newArrival, responseTime, queueLength, timeY, timeN, optional, serviceTime, avgServiceTimeSetpoint):
        if newArrival:
            self.avgServiceTimeSetpoint = avgServiceTimeSetpoint
            self.nbrRunningRequests += 1
        if optional and not newArrival:
            self.latestServiceTimes.append(serviceTime)

    def decidePacketRequest(self):
        actuationDiff = int(int(self.ctrl) - self.ctrlActuated)
        self.ctrlActuated = int(self.ctrl)

        packetReq = int(actuationDiff + 1)

        self.nbrRunningRequests -= 1

        return packetReq

    def __str__(self):
        return self.name
