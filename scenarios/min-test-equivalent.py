import scipy.stats as stats
import numpy as np
from base.numerical_dist import NumericalDistribution

s1dist = NumericalDistribution(cdf_location='dists/mintest.csv', seed=21515)

avgServiceRate = 1.0/1.151
addServer(at=0.0, serviceTimeDistribution=s1dist)

setRate(at = 0, rate = 0.7*avgServiceRate)


endOfSimulation(at = 1000000)
