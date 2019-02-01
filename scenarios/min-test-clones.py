import scipy.stats as stats
import numpy as np
from base.numerical_dist import NumericalDistribution

s1dist = stats.norm(loc=1.8, scale=0.5)
s1dist.random_state = np.random.RandomState(seed=5418189)
s2dist = stats.expon(scale=1.0/0.4)
s2dist.random_state = np.random.RandomState(seed=4535)
s3dist = stats.uniform(loc=1.0, scale=2.0)
s3dist.random_state = np.random.RandomState(seed=38883)

avgServiceRate = 1.0/1.151

addServer(at=0.0, serviceTimeDistribution=s1dist)
addServer(at=0.0, serviceTimeDistribution=s2dist)
addServer(at=0.0, serviceTimeDistribution=s3dist)

setRate(at = 0, rate = 0.7*avgServiceRate)


endOfSimulation(at = 1000000)
