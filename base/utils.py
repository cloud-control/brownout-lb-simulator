from __future__ import division, print_function
import numpy as np
import math
import csv



# for numpy >= 1.7
# from numpy.random import choice

## Randomly picks an item from several choices, as given by the attached
# weights. Sum of weight must equal 1.
# Example: @code weightedChoice([('a', 0.1), ('b', 0.9)]) @endcode
#
# @param choiceWeightPairs list of pairs to choose from; first item in pair is
# choice, second is weight
def weightedChoice(choiceWeightPairs, rng):
    # for numpy >= 1.7
    # weights  = [w for c,w in choiceWeightPairs]
    # elements = [c for c,w in choiceWeightPairs]
    # weights  = [w/sum(weights) for w in weights]
    # return choice(elements, p=weights)
    totalWeight = sum(weight for choice, weight in choiceWeightPairs)
    rnd = rng.uniform(0, totalWeight)
    upto = 0
    for choice, weight in choiceWeightPairs:
        if upto + weight > rnd:
            return choice
        upto += weight
    assert False, "Shouldn't get here"  # pragma: no cover


## Computes average
# @param numbers list of number to compute average for
# @return average or NaN if list is empty
def avg(numbers):
    if len(numbers) == 0:
        return float('nan')
    return sum(numbers) / len(numbers)


## Computes maximum
# @param numbers list of number to compute maximum for
# @return maximum or NaN if list is empty
# @note Similar to built-in function max(), but returns NaN instead of throwing
# exception when list is empty
def maxOrNan(numbers):
    if len(numbers) == 0:
        return float('nan')
    return max(numbers)


## Normalize a list, so that the sum of all elements becomes 1
# @param numbers list to normalize
# @return normalized list
def normalize(numbers):
    if len(numbers) == 0:
        # Nothing to do
        return []

    s = sum(numbers)
    if s == 0:
        # How to normalize a zero vector is a matter of much debate
        return [float('nan')] * len(numbers)
    return [n / s for n in numbers]


def getDistInfo(dist, util, cloneFactor):
    xmax = 100
    N = 1000000
    h = 1 / (N / xmax)
    x = np.linspace(0, xmax, N)

    if dist == "uniform":
        a = 0.0
        b = 2.0

        oneslen = int(N - b/xmax*N)
        ones = np.ones(oneslen)
        x_tmp = x[0:(N-oneslen)]
        F1_tmp = (x_tmp-a)/(b-a)

        F1 = np.concatenate((F1_tmp, ones))

        Fmin = 1 - np.power(1 - F1, cloneFactor)

        avg_servicetime = h * np.cumsum(1 - Fmin)
        avg_s = avg_servicetime[-1]
        mu_cf = 1 / avg_s
        lambd = mu_cf * util / cloneFactor

        return lambd, avg_s

    elif dist == "SXmodel":
        dollycdf = np.array([0, 0.23, 0.37, 0.46, 0.49, 0.57, 0.67, 0.71, 0.85, 0.97, 0.9910, 0.9980, 1.00])

        hypermeanservicetime = 1.0 / 4.7

        mindollycdf = 1 - np.power(1 - dollycdf, cloneFactor)

        cloneminmean = np.cumsum(1 - mindollycdf)

        avg_s = hypermeanservicetime * cloneminmean[-1]
        mu_cf = 1 / avg_s

        lambd = mu_cf * util / cloneFactor

        return lambd, avg_s

    elif dist == "expon":
        avg_s = 1.0 / cloneFactor
        lambd = util

        return lambd, avg_s

    elif dist == "weibull_min":
        shape = 0.5
        scale = 0.5
        F1 = 1 - np.exp(-1*np.power(x/scale, shape))

        Fmin = 1 - np.power(1 - F1, cloneFactor)

        avg_servicetime = h * np.cumsum(1 - Fmin)
        avg_s = avg_servicetime[-1]
        mu_cf = 1 / avg_s
        lambd = mu_cf * util / cloneFactor

        return lambd, avg_s

    elif dist == "pareto":
        shape = 2.5
        scale = 0.6
        zerolen = int(0.6/h - 1)
        zeros = np.zeros(zerolen)
        x_tmp = x[zerolen:]
        F1_tmp = 1 - np.power(scale / x_tmp, shape)

        F1 = np.concatenate((zeros, F1_tmp))

        Fmin = 1 - np.power(1 - F1, cloneFactor)

        avg_servicetime = h * np.cumsum(1 - Fmin)
        avg_s = avg_servicetime[-1]
        mu_cf = 1 / avg_s
        lambd = mu_cf * util / cloneFactor

        return lambd, avg_s

def getMeanServiceTime(dist, cloneFactor):
    lambd, avg_s = getDistInfo(dist, 0.5, cloneFactor)
    return avg_s

def getLambdaFrac(dist, util, cloneFactor):
    lambd, avg_s = getDistInfo(dist, util, cloneFactor)
    return lambd


def readCsv(filename):
    cdfvec = []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for v in reader:
            row = [float(v[0]), float(v[1])]
            cdfvec.append(row)
    return cdfvec
