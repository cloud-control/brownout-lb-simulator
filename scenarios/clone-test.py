from scipy.stats import expon
import numpy as np

nbrServers = 12
for i in range(0, nbrServers):
    #serviceRate = 1.0
    #dist = expon(scale=1.0/serviceRate)
    #dist.random_state = np.random.RandomState(seed=i*3)
    dist = None
    addServer(at=0.0, serviceTimeDistribution=dist)

setRate(at =    0, rate = 0.30*nbrServers)

endOfSimulation(at = 10000)
