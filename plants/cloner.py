from __future__ import division

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

        self.seed = seed

        self.cloneStd = 1.0

        self.cloning = 0

        self.random = xxx_random.Random()
        self.random.seed(seed)

        np.random.seed(seed)

        self.minimumServiceTime = 0.0001

        self.activeRequests = {}

    def clone(self, request, queues, servers):
        if not self.cloning:
            return None



        #targetIndex= [index for index, queue in enumerate(queues) if index != request.chosenBackendIndex]
        #print queues
        #print "------------------------"
        #print targetIndex

        #targetServer = servers[targetIndex[0]]

        #print targetServer.activeRequests
        #print targetServer.waitingRequests

        shouldClone = True
        propClones = 0.0

        """if targetServer.activeRequests:
            nbrActiveClones = sum(req.isClone == 1 for req in targetServer.activeRequests)
            nbrClones = nbrActiveClones
            propClones = nbrClones / (len(targetServer.activeRequests))

            shouldClone = propClones < 0.1"""

        currentClones = self.getClones(request)

        nbrClones = 0
        if currentClones:
            nbrClones = len(currentClones)

        if nbrClones < len(servers):
            shouldClone = True
        else:
            shouldClone = False

        #shouldClone = self.random.random() < 1.1

        #print propClones
        #print shouldClone
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
            for i in range(0, len(clones)):
                #print i
                if not hasattr(clones[i], 'serviceTime'):
                    #serviceTime = self.random.uniform(mean/corrfactor, mean*corrfactor)
                    minval = mean/corrfactor
                    maxval = mean*corrfactor
                    if corrfactor == 1.0:
                        serviceTime = mean
                    else:
                        serviceTime = np.random.exponential(0.01)  # zero correlation between clones!
                        #if serviceTime < 0.00001:
                        #    print "Service time too small!: " + str(serviceTime)

                        #serviceTime = self.drawCloneServiceTime(x_s, cdf)
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

        #print "Trying to cancel clones for req " + str(request.requestId)
        key = request.requestId
        if key in self.activeRequests:
            #print "Cancels clones for req id " + str(request.requestId)
            #for clone in self.activeRequests[key]:
                #print clone.serviceTime
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

