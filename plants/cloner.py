from __future__ import division
import csv
import math
import numpy as np
import random as xxx_random # prevent accidental usage
import scipy.stats as st
from scipy import integrate
from scipy.stats import norm

from base import Request
from base.utils import *

# Simulates a request cloner.
class Cloner:

    ## Constructor.
    def __init__(self, seed=1):

        self.seed = 65184

        self.cloneStd = 1.0

        self.cloning = 0
        self.nbrClones = 1

        self.random = xxx_random.Random()
        self.random.seed(self.seed)

        np.random.seed(self.seed)

        self.minimumServiceTime = 0.0001

        self.activeRequests = {}

        self.serviceCounter = 0
        self.minServiceTime = 0.0

        self.minSlowdown = 1.0
        self.slowdownCounter = 0

        self.backends = []

        self.cdf = np.asarray(self.readCsv('/local/home/tommi/CloudControl/cloning/brownout-lb-simulator/matlab/umin.csv'))
        self.x = np.asarray(self.readCsv('/local/home/tommi/CloudControl/cloning/brownout-lb-simulator/matlab/x.csv'))
        self.dolly = np.asarray(self.readCsv('/local/home/tommi/CloudControl/cloning/brownout-lb-simulator/matlab/dolly.csv'))

    def readCsv(self, filename):
        floatvector = []
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            for v in reader:
                floatvector.append(float(v[0]))
        return floatvector

    def setCloning(self, cloning):
        self.cloning = cloning

    def setNbrClones(self, nbrClones):
        self.nbrClones = nbrClones

    def clone(self, request, queues, servers):
        if not self.cloning:
            return None
        self.backends = servers

        currentClones = self.getClones(request)
        nbrClones = 1
        if currentClones:
            nbrClones = len(currentClones)

        diff = self.nbrClones - nbrClones
        if diff >= 1.0:
            shouldClone = True
        elif (diff < 1.0) and (diff > 0.0):
            shouldClone = self.random.uniform(0, 1) <= diff
        else:
            shouldClone = False

        key = request.requestId

        if not shouldClone:
            if key not in self.activeRequests:
                self.activeRequests[request.requestId] = [request]
            return None

        request.isClone = False
        clone = Request()
        clone.createdAt = request.createdAt
        clone.requestId = request.requestId
        clone.originalRequest = request.originalRequest
        clone.isClone = True
        clone.illegalServers = []
        #print "Got to clone method"
        #print "Original req id is " + str(request.requestId)
        #print "Adding clone with req id " + str(clone.requestId)
        clones = []
        key = request.requestId
        if key in self.activeRequests:
            clones = self.activeRequests[request.requestId]

        if clones:
            for i in range(0, len(clones)):
                clone.illegalServers.append(clones[i].chosenBackendIndex)
            self.activeRequests[request.requestId].append(clone)
        else:
            self.activeRequests[request.requestId] = [request, clone]
            clone.illegalServers.append(request.chosenBackendIndex)

        #print "Clone " + str(clone.requestId) + " illegal server length: " + str(len(clone.illegalServers))
        return clone

    def setCloneServiceTimes(self, request, mean):
        if not self.cloning:
            return

        def inRange(minval, maxval, val):
            if val > maxval:
                return False
            if val < minval:
                return False
            return True

        corrfactor = 10000.0
        mu = 0.01
        sigma = 1

        #x_s, cdf = self.calculateCDF(mu, sigma, mean)

        key = request.requestId
        if key in self.activeRequests:
            clones = self.activeRequests[request.requestId]
            #print self.activeRequests
            taskSize = self.drawHyperExpServiceTime()
            #print "Req " + str(key) + ": " + str(taskSize)
            serviceTimes = []
            slowdowns = []
            for i in range(0, len(clones)):
                if not hasattr(clones[i], 'serviceTime'):
                    #serviceTime = self.random.uniform(mean/corrfactor, mean*corrfactor)
                    minval = mean/corrfactor
                    maxval = mean*corrfactor
                    if corrfactor == 1.0:
                        serviceTime = mean
                    else:
                        #serviceTime = np.random.exponential(0.01)  # zero correlation between clones!
                        #if serviceTime < 0.00001:
                        #    print "Service time too small!: " + str(serviceTime)
                        #serviceTime = self.drawCloneServiceTime(self.x, self.cdf)
                        slowdown = self.drawDollySlowdown()
                        #slowdown = 4.7
                        serviceTime = slowdown*taskSize
                        serviceTimes.append(serviceTime)
                        slowdowns.append(slowdown)
                        #print "clone req " + str(clones[i].requestId) + " service time " + str(serviceTime)
                        #print "------------------------------------------------------"
                        #print "Orig service time: " + str(mean)
                        #print "Clone service time: " + str(serviceTime)
                        #print "------------------------------------------------------"
                        #serviceTime = -1.0
                        #while not inRange(minval, maxval, serviceTime):
                            #serviceTime = np.random.exponential(0.01)

                        #print "Service time for clone of req id " + str(request.requestId) + " is " + str(serviceTime)

                    #serviceTime = np.random.exponential(0.01) # zero correlation between clones!

                    self.activeRequests[request.requestId][i].serviceTime = serviceTime

                    #print "setting service time for clone with reqid " + str(clones[i].requestId) + " to " + str(serviceTime)

            self.minServiceTime = (self.minServiceTime * self.serviceCounter + min(serviceTimes)) / (self.serviceCounter + 1)
            self.minSlowdown = (self.minSlowdown * self.serviceCounter + min(slowdowns)) / (self.serviceCounter + 1)
            #print self.minServiceTime
            self.serviceCounter += 1
            #print self.serviceCounter

    def getClones(self, request):
        if not self.cloning:
            return None

        #print "got to getClones with reqid " + str(request.requestId)
        key = request.requestId
        if key in self.activeRequests:
            clones = self.activeRequests[key]
            return clones
        else:
            return None

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

        #print request.isCompleted

        #print "Trying to cancel clones for req " + str(request.requestId)
        key = request.requestId
        if key in self.activeRequests:
            #print "Cancels clones for req id " + str(request.requestId)
            #for clone in self.activeRequests[key]:
                #print clone.serviceTime

            clones = self.activeRequests[request.requestId]
            #print clones

            for i in range(0, len(clones)):
                clone = clones[i]
                if not hasattr(clone, 'isCompleted'):
                    #print clone.chosenBackend
                    clone.chosenBackend.onCanceled(clone)
                #else:
                    #print "completed server: " + str(clone.chosenBackend)

            del self.activeRequests[key]
        #else:
            #print "Key not in list!"

    def calculateCDF(self, mu, sigma, mean):
        N = 10000  # nbr of grid points in pdf/cdf
        xmax = 20*mean
        xmin = 0.0
        h = (xmax-xmin)/N
        x_s = np.linspace(xmin, xmax, N)
        sig = sigma*mu

        pdf = np.exp(np.subtract(np.divide(-np.square(np.subtract(x_s, mean)), 2*sig**2), np.divide(x_s, mu)))
        normalized = np.sum(pdf)*h
        pdf = np.divide(pdf, normalized)
        cdf = h*integrate.cumtrapz(pdf)

        return x_s, cdf

    def drawHyperExpServiceTime(self):
        coeff = 10.0
        hypermean = 1 / 4.7
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

    def drawCloneServiceTime(self, x_s, cdf):

        inverse_point = cdf[-1]*np.random.uniform()

        return self.cdfInverter(x_s, cdf, inverse_point)

    def cdfInverter(self, x_s, cdf, inv_point):
        N = x_s.size
        x_u = N
        x_l = 0
        x_i = int(math.floor((x_u - x_l) / 2))
        x_i_prev = -1

        while x_i != x_i_prev:
            if cdf[x_i] > inv_point:
                x_u = x_i
            elif cdf[x_i] < inv_point:
                x_l = x_i

            x_i_prev = x_i
            x_i = int(math.floor((x_u - x_l) / 2) + x_l)

        if x_u == x_l:
            x_u = x_l + 1

        total_diff = cdf[x_u] - cdf[x_l]
        diff = inv_point - cdf[x_l]

        if total_diff < 0.00001:
            # Use upper value
            icdf = x_s[x_u]
        else:
            icdf = x_s[x_l] + (diff / total_diff) * (x_s[x_u] - x_s[x_l])

        return icdf

