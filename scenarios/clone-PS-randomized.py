import scipy.stats
import numpy as np
from base.numerical_dist import NumericalDistribution

nbrServers = nbrOfServers
seed = setSeed
for i in range(0, nbrServers):

    if dist == "uniform":
        try:
            func = getattr(scipy.stats, dist)
        except:
            raise ValueError("Distribution could not load, does it exist in scipy.stats?")
        serviceTimeDistribution = func(scale=2.0, loc=0.000001)
        serviceTimeDistribution.random_state = np.random.RandomState(seed=seed + i*2+45567)
    elif dist == "expon":
        try:
            func = getattr(scipy.stats, dist)
        except:
            raise ValueError("Distribution could not load, does it exist in scipy.stats?")
        serviceTimeDistribution = func()
        serviceTimeDistribution.random_state = np.random.RandomState(seed=seed + i*2+45567)
    elif dist == "pareto":
        try:
            func = getattr(scipy.stats, dist)
        except:
            raise ValueError("Distribution could not load, does it exist in scipy.stats?")
        serviceTimeDistribution = func(scale=0.6, b=2.5)
        serviceTimeDistribution.random_state = np.random.RandomState(seed=seed + i*2+45567)
    elif dist == "weibull_min":
        try:
            func = getattr(scipy.stats, dist)
        except:
            raise ValueError("Distribution could not load, does it exist in scipy.stats?")
        serviceTimeDistribution = func(scale=0.5, c=0.5)
        serviceTimeDistribution.random_state = np.random.RandomState(seed=seed + i*2+45567)
    else:
        serviceTimeDistribution = None

    addServer(at=0.0, serviceTimeDistribution=serviceTimeDistribution,
              meanStartupDelay=arrivalDelay, meanCancellationDelay=cancellationDelay)


changeMC(at=0.0, newMC=10000)
setRate(at = 0, rate = arrivalRateFrac*serviceRate*nbrServers)
endOfSimulation(at = 1000000/(arrivalRateFrac*nbrServers))

