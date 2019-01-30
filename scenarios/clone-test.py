import scipy.stats
import numpy as np
import sys
from base.numerical_dist import NumericalDistribution

print(dist)
print(serviceRate)
print(arrivalRateFrac)

nbrServers = 12
for i in range(0, nbrServers):

    if dist == "fromPath":
        serviceTimeDistribution = NumericalDistribution(distpath)
    elif dist != "SXmodel":
        try:
            func = getattr(scipy.stats, dist)
        except:
            raise ValueError("Distribution could not load, does it exist in scipy.stats?")
        serviceTimeDistribution = func(scale=1.0/serviceRate)

    else:
        serviceTimeDistribution = None

    #serviceRate = 1.0
    #dist = expon(scale=1.0/serviceRate)
    #dist.random_state = np.random.RandomState(seed=i*3)

    addServer(at=0.0, serviceTimeDistribution=serviceTimeDistribution)

print("Got here 3")

setRate(at = 0, rate = arrivalRateFrac*serviceRate*nbrServers)


endOfSimulation(at = 10000)
