from __future__ import division
import csv
import math
import numpy as np
import random as xxx_random # prevent accidental usage
from base import Request
from base.utils import *
from collections import OrderedDict

# Simulates a request cloner.
class Cloner:

    def __init__(self, setSeed=123):
        self.seed = setSeed

        self.cloning = 0
        self.nbrClones = 1

        self.random = xxx_random.Random()
        self.random.seed(self.seed)

        self.activeRequests = {}

        self.servers = None

        self.dolly = np.asarray(self.readCsv('dists/dolly.csv'))

        self.processorShareVarCoeff = 0.0
        self.processorShareMean = 0.0

        self.mapping = {}

        self.reqNbr = 0

        self.sim = None

        # Statistics
        self.serviceCounter = 0
        self.minServiceTime = 0.0
        self.minSlowdown = 1.0

    def setSim(self, sim):
        self.sim = sim

    def setServers(self, servers):
        self.servers = servers

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

        processorShares = []
        thetas = []
        incompleteCloneServerIndexes = []

        for i in range(0, len(clones)):
            clone = clones[i]

            if not hasattr(clone, 'isCompleted') and hasattr(clone, 'chosenBackendIndex'):
                incompleteCloneServerIndexes.append(clone.chosenBackendIndex)


            if not hasattr(clone, 'isCompleted') and hasattr(clone, 'chosenBackend'):
                if hasattr(clone, 'lastCheckpoint'):
                    clone.chosenBackend.updateAvgProcessorShare(clone)

                clone.isCanceled = True
                clone.chosenBackend.onCanceled(clone)

            if hasattr(clone, 'avgProcessorShare'):
                processorShares.append(clone.avgProcessorShare)
                thetas.append(clone.theta)


        #incompleteServers = [s for i,s in enumerate(self.servers) if i in incompleteCloneServerIndexes]

        #for s in incompleteServers:
        #    lastQueue = s.nbrRequests[-1][1]

        #    s.nbrRequests.append((self.sim.now, lastQueue-1))

        N = sum(thetas)
        Mvec = []

        arr = clones[0].arrival
        dep = self.sim.now


        """for server in self.servers:
            print "--------------------"
            print server.nbrRequests
            print "--------------------"

        print "arr: " + str(arr)
        print "dep: " + str(dep)"""

        for server in self.servers:
            for i, val in reversed(list(enumerate(server.nbrRequests))):
                if self.floatLessThanOrEqual(server.nbrRequests[i][0], arr):
                    """print "-------------------"
                    print "arr = " + str(arr)
                    print server.nbrRequests[i][0]
                    print "-------------------"""""
                    if i == len(server.nbrRequests) - 1:
                        M = float(server.nbrRequests[i][1])
                        Mvec.append(M)
                        break
                    j = i + 1

                    ttot = 0
                    M = 0.0

                    while self.floatLessThanOrEqual(server.nbrRequests[j][0], dep):
                        if ttot == 0:
                            t = server.nbrRequests[j][0] - arr
                        else:
                            t = server.nbrRequests[j][0] - server.nbrRequests[j-1][0]

                        if t > 0.0:
                            M = (M*ttot + (server.nbrRequests[j-1][1])*t)/(ttot+t)
                            ttot = ttot + t
                        if j < (len(server.nbrRequests) - 1):
                            j = j + 1
                        else:
                            break

                    t = dep - server.nbrRequests[j][0]

                    M = (M * ttot + (server.nbrRequests[j][1]) * t) / (ttot + t)
                    Mvec.append(M)
                    break

        M = sum(Mvec)
        """print "------------"      
        print "M = " + str(M)
        print "N = " + str(N)
        print "------------"""""

        roundedM = round(float(M), 1)
        roundedN = round(float(N), 4)
        if roundedM not in self.mapping:
            self.mapping[roundedM] = (roundedN, 1)
        else:
            newN = (self.mapping[roundedM][0]*self.mapping[roundedM][1] + roundedN)/(self.mapping[roundedM][1] + 1)
            newRoundedN = round(newN, 3)
            newCount = self.mapping[roundedM][1] + 1

            self.mapping[roundedM] = (newRoundedN, newCount)


        """print "------------"
        print self.mapping
        print "------------"""""

        self.processorShareMean = (self.processorShareMean*self.reqNbr + avg(processorShares))/(self.reqNbr+1)
        self.processorShareVarCoeff = (self.processorShareVarCoeff*self.reqNbr + np.std(processorShares)/avg(processorShares))/(self.reqNbr+1)

        self.reqNbr += 1

        self.deleteClones(request)

    def floatLessThanOrEqual(self, f1, f2):
        tol = 0.00001
        if f1<f2:
            return True
        elif abs(f1 - f2) <= tol:
            return True
        else:
            return False

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
                slowdownFactor = clones[i].chosenBackend.dollySlowdown
                slowdown = self.drawDollySlowdown(slowdownFactor)
                serviceTime = slowdown*taskSize
                #serviceTime = self.drawHyperExpServiceTime()
                #serviceTime = 0.743
                #serviceTime = slowdown*1.0/4.7
                #serviceTime = self.random.expovariate(1.0)
                #serviceTime = self.drawHyperExpServiceTime(p=0.0081, mu1=0.0764, mu2=0.5236)#m3=150
                #serviceTime = self.drawHyperExpServiceTime(p=0.1000, mu1=0.2000, mu2=0.6000)#m3=100
                #serviceTime = self.drawHyperExpServiceTime(p=0.6581, mu1=0.3675, mu2=1.6325)#m3=80
                #serviceTime = 2.9427*taskSize
                #serviceTime = 0.50
                #serviceTime = taskSize*4.7
                #serviceTime = 1.0 + self.random.expovariate(1.0)
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

    def drawHyperExpServiceTime(self, p=None, mu1=None, mu2=None):

        if p is None:
            coeff = 2.0
            hypermean = 1.0/4.7
            #hypermean = 1.0
            p1 = 0.5 * (1.0 + math.sqrt((coeff - 1.0) / (coeff + 1.0)))
            p2 = 1.0 - p1
            mu1 = 2.0 * p1 / hypermean
            mu2 = 2.0 * p2 / hypermean

            if self.random.uniform(0, 1) <= p1:
                return self.random.expovariate(mu1)
            else:
                return self.random.expovariate(mu2)
        else:
            if self.random.uniform(0, 1) <= p:
                return self.random.expovariate(mu1)
            else:
                return self.random.expovariate(mu2)

    def drawDollySlowdown(self, slowdownFactor):
        slowint = self.random.randint(0, 999)
        slowdown = self.dolly.item(slowint)
        return slowdown*slowdownFactor

    def readCsv(self, filename):
        floatvector = []
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            for v in reader:
                floatvector.append(float(v[0]))
        return floatvector

