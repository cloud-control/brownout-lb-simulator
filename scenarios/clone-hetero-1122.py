import scipy.stats
import numpy as np
from base.numerical_dist import NumericalDistribution


addServer(at=0.0, serviceTimeDistribution=None, dollySlowdown=1)
addServer(at=0.0, serviceTimeDistribution=None, dollySlowdown=1)

addServer(at=0.0, serviceTimeDistribution=None, dollySlowdown=2)
addServer(at=0.0, serviceTimeDistribution=None, dollySlowdown=2)

nbrServers = 4

changeMC(at=0.0, newMC=1)
setRate(at = 0, rate = arrivalRateFrac*serviceRate*nbrServers)


endOfSimulation(at = 1000000/(arrivalRateFrac*nbrServers))
