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
        self.serviceTimeSetpoint = 0.40
        self.serviceTimeError = 0.0
        self.ctrlActuated = 0

        self.ctrl = 0.0

        self.K = 4.8532
        self.Ti = 0.7213
        self.beta = 1.0
        self.Tr = 10.0
        self.integralPart = 0.0
        self.estimatedProcessGain = 0.05

        self.latestServiceTimes = []

        ## Random number generator
        self.random = xxx_random.Random()
        self.random.seed(seed)

        if self.controlPeriod > 0:
            self.sim.add(0, self.runControlLoop)

    ## Runs the periodical control loop
    def runControlLoop(self):

        # Filter service times
        alpha_s = 0.5
        if self.latestServiceTimes:
            self.filteredServiceTime = (1 - alpha_s) * self.filteredServiceTime + alpha_s * avg(self.latestServiceTimes)

        # Estimate process gain (relation between nbr of packets being served and the service time)
        alpha_p = 0.5
        if self.latestServiceTimes:
            self.estimatedProcessGain = (1 - alpha_p) * self.estimatedProcessGain + \
                alpha_p * avg(self.latestServiceTimes) / (self.ctrlActuated + 1)

        # Adaptive service time PI controller (keeps filter pole at a and places integrator pole at location b)
        a = -math.log(1 - alpha_s) / self.controlPeriod
        b = 0.3
        Kp = self.estimatedProcessGain

        kp = b * (1 - alpha_s) / (alpha_s * alpha_s * b * Kp + Kp * a - Kp * alpha_s * a - Kp * alpha_s * b)
        ki = b * (1 + Kp * alpha_s * kp)/Kp

        self.K = kp
        self.Ti = kp / ki

        self.serviceTimeError = self.serviceTimeSetpoint - self.filteredServiceTime
        proportionalPart = self.K * (self.beta * self.serviceTimeSetpoint - self.filteredServiceTime)
        # proportionalPart = 0.0
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
            self.estimatedProcessGain,
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
        actuationDiff = int(int(self.ctrl) - self.ctrlActuated)
        self.ctrlActuated = int(self.ctrl)

        packetReq = int(actuationDiff + 1)
        # packetReq = 1
        return packetReq

    def __str__(self):
        return self.name
