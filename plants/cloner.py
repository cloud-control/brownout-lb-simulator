from __future__ import division
import csv
import math
import numpy as np
import random as xxx_random # prevent accidental usage
from base import Request


# Simulates a request cloner.
class Cloner:

    def __init__(self):
        self.seed = 65184

        self.cloning = 0
        self.nbrClones = 1

        self.random = xxx_random.Random()
        self.random.seed(self.seed)

        self.activeRequests = {}

        self.dolly = np.asarray(self.readCsv('dists/dolly.csv'))

        # Statistics
        self.serviceCounter = 0
        self.minServiceTime = 0.0
        self.minSlowdown = 1.0

    def setCloning(self, cloning):
        self.cloning = cloning

    def setNbrClones(self, nbrClones):
        self.nbrClones = nbrClones

    def clone(self, request):
        if not self.cloning:
            return None

        shouldClone = self.shouldClone(request)

        if not shouldClone:
            key = request.requestId
            if key not in self.activeRequests:
                self.activeRequests[request.requestId] = [request]
            return None

        clone = self.createClone(request)
        otherClones = self.getClones(request)

        self.setIllegalServers(request, clone, otherClones)

        return clone

    def isCanceled(self, request):
        if not self.cloning:
            return False

        key = request.requestId
        if key in self.activeRequests:
            return False
        else:
            return True

    def cancelAllClones(self, request):
        if not self.cloning:
            return

        clones = self.getClones(request)
        if not clones:
            return

        for i in range(0, len(clones)):
            clone = clones[i]
            if not hasattr(clone, 'isCompleted') and hasattr(clone, 'chosenBackend'):
                clone.chosenBackend.onCanceled(clone)

        self.deleteClones(request)

    def setCloneServiceTimes(self, request):
        if not self.cloning:
            return

        clones = self.getClones(request)

        if not clones:
            return

        taskSize = self.drawHyperExpServiceTime()
        serviceTimes = []
        slowdowns = []
        for i in range(0, len(clones)):
            if not hasattr(clones[i], 'serviceTime'):
                slowdown = self.drawDollySlowdown()
                serviceTime = slowdown*taskSize
                self.activeRequests[request.requestId][i].serviceTime = serviceTime
                serviceTimes.append(serviceTime)
                slowdowns.append(slowdown)

        # Uncomment to print service time statistics
        #self.minServiceTime = (self.minServiceTime * self.serviceCounter + min(serviceTimes)) / (self.serviceCounter + 1)
        #self.minSlowdown = (self.minSlowdown * self.serviceCounter + min(slowdowns)) / (self.serviceCounter + 1)
        #print self.minServiceTime
        #self.serviceCounter += 1
        #print self.serviceCounter

    def shouldClone(self, request):
        currentNbrClones = self.getNbrClones(request)
        diff = self.nbrClones - currentNbrClones
        if diff >= 1.0:
            return True
        elif (diff < 1.0) and (diff > 0.0):
            return self.random.uniform(0, 1) <= diff
        else:
            return False

    def createClone(self, request):
        clone = Request()
        clone.createdAt = request.createdAt
        clone.requestId = request.requestId
        clone.originalRequest = request.originalRequest
        clone.isClone = True
        clone.illegalServers = []

        return clone

    def getNbrClones(self, request):
        currentClones = self.getClones(request)
        nbrClones = 1
        if currentClones:
            nbrClones = len(currentClones)

        return nbrClones

    def setIllegalServers(self, request, clone, otherClones):
        if otherClones:
            for i in range(0, len(otherClones)):
                clone.illegalServers.append(otherClones[i].chosenBackendIndex)
            self.activeRequests[request.requestId].append(clone)
        else:
            self.activeRequests[request.requestId] = [request, clone]
            clone.illegalServers.append(request.chosenBackendIndex)

    def getClones(self, request):
        if not self.cloning:
            return None

        key = request.requestId
        if key in self.activeRequests:
            clones = self.activeRequests[key]
            return clones
        else:
            return None

    def deleteClones(self, request):
        del self.activeRequests[request.requestId]

    def drawHyperExpServiceTime(self):
        coeff = 10.0
        hypermean = 1.0 / 4.7
        p1 = 0.5 * (1.0 + math.sqrt((coeff - 1.0) / (coeff + 1.0)))
        p2 = 1.0 - p1
        mu1 = 2.0 * p1 / hypermean
        mu2 = 2.0 * p2 / hypermean

        if self.random.uniform(0, 1) <= p1:
            return self.random.expovariate(mu1)
        else:
            return self.random.expovariate(mu2)

    def drawDollySlowdown(self):
        slowint = self.random.randint(0, 999)
        slowdown = self.dolly.item(slowint)
        return slowdown

    def readCsv(self, filename):
        floatvector = []
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            for v in reader:
                floatvector.append(float(v[0]))
        return floatvector

