import scipy.stats
import numpy as np
from base.numerical_dist import NumericalDistribution

nbrServers = nbrOfServers #12
for i in range(0, nbrServers):

    if dist == "fromPath":
        serviceTimeDistribution = NumericalDistribution(cdf_location=distpath, seed=i*3 + setSeed + 123)
    elif dist != "SXmodel":
        try:
            func = getattr(scipy.stats, dist)
        except:
            raise ValueError("Distribution could not load, does it exist in scipy.stats?")
        serviceTimeDistribution = func(scale=1.0/serviceRate)
        serviceTimeDistribution.random_state = np.random.RandomState(seed=i*3+45567 + setSeed + 456)

    else:
        serviceTimeDistribution = None

    addServer(at=0.0, serviceTimeDistribution=serviceTimeDistribution)

changeMC(at=0.0, newMC=1000000)
setRate(at = 0, rate = arrivalRateFrac*serviceRate*nbrServers)


endOfSimulation(at = 1000000/(arrivalRateFrac*nbrServers))