import math
import numpy as np
import csv
import random as xxx_random


class NumericalDistribution:

    def __init__(self, cdf_location=None, seed=1):
        cdf = np.asarray(self.readCsv(cdf_location))
        self.cdf_x = cdf[:, 0]
        self.cdf_y = cdf[:, 1]
        self.max_cdf = self.cdf_y[-1]

        # Uncomment here if to use pre-inverted cdf
        #self.icdf = {}
        #self.invertCdf()
        #self.h = 0.00001
        #self.icdfSize = 99999

        self.random = xxx_random.Random()
        self.random.seed(seed)

    def invertCdf(self):
        for i in range(0, self.icdfSize):
            point = i*self.h
            invertedPoint = self.invertPoint(point)
            self.icdf[point] = invertedPoint

    def rvs(self):
        # Uncomment here if to use pre-inverted cdf
        #key = float(self.random.randint(0, self.icdfSize-1)*self.h)
        #return self.icdf[key]

        point = self.random.random()*self.max_cdf
        return self.invertPoint(point)

    def invertPoint(self, point):
        N = self.cdf_x.size
        x_u = N-1
        x_l = 0
        x_i = int(math.floor((x_u - x_l) / 2))
        x_i_prev = -1

        while x_i != x_i_prev:
            if self.cdf_y[x_i] > point:
                x_u = x_i
            elif self.cdf_y[x_i] < point:
                x_l = x_i

            x_i_prev = x_i
            x_i = int(math.floor((x_u - x_l) / 2) + x_l)

        if x_u == x_l:
            x_u = x_l + 1

        total_diff = self.cdf_y[x_u] - self.cdf_y[x_l]
        diff = point - self.cdf_y[x_l]

        if total_diff < 0.00001:
            # Use upper value
            invertedPoint = self.cdf_x[x_u]
        else:
            invertedPoint = self.cdf_x[x_l] + (diff / total_diff) * (self.cdf_x[x_u] - self.cdf_x[x_l])

        return invertedPoint

    def readCsv(self, filename):
        cdfvec = []
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            for v in reader:
                row = [float(v[0]), float(v[1])]
                cdfvec.append(row)
        return cdfvec

