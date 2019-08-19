import scipy.stats as stats
import numpy as np
from base.numerical_dist import NumericalDistribution

nbrServers = nbrOfServers #12
"""
for i in range(0, nbrServers):

    if dist == "fromPath":
        serviceTimeDistribution = NumericalDistribution(cdf_location=distpath, seed=i*3+1852441)
    elif dist != "SXmodel":
        try:
            func = getattr(scipy.stats, dist)
        except:
            raise ValueError("Distribution could not load, does it exist in scipy.stats?")
        serviceTimeDistribution = func(scale=1.0/serviceRate)
        serviceTimeDistribution.random_state = np.random.RandomState(seed=i*3+45567)

    else:
        serviceTimeDistribution = None

    addServer(at=0.0, serviceTimeDistribution=serviceTimeDistribution)
"""

s1dist = stats.expon(scale=1/0.48)
s1dist.random_state = np.random.RandomState(seed=1*3 + setSeed)

s2dist = stats.uniform(loc=0.5, scale=3)
s2dist.random_state = np.random.RandomState(seed=2*3 + setSeed)

s3dist = stats.weibull_min(3, scale=2)
s3dist.random_state = np.random.RandomState(seed=3*3 + setSeed)

addServer(at=0.0, serviceTimeDistribution=s1dist)
addServer(at=0.0, serviceTimeDistribution=s2dist)
addServer(at=0.0, serviceTimeDistribution=s3dist)

changeMC(at=0.0, newMC=1)
setRate(at = 0, rate = arrivalRateFrac*serviceRate*1)

endOfSimulation(at = 1000000/(arrivalRateFrac*1))