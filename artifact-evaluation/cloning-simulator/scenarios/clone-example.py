import scipy.stats
import numpy as np
from base.numerical_dist import NumericalDistribution

nbrServers = nbrOfServers
seed = setSeed

# The scenario script is executed from within simulator.py, and gives an easy and general way of setting up the servers
# in the system, as well as meta-parameters such as simulation time and queueing discipline.

for i in range(0, nbrServers):

    if dist == "fromPath":
        serviceTimeDistribution = NumericalDistribution(cdf_location=distpath, seed=seed+i*2+45567)
    elif dist != "SXmodel":
        try:
            func = getattr(scipy.stats, dist)
        except:
            raise ValueError("Distribution could not load, does it exist in scipy.stats?")
        serviceTimeDistribution = func(scale=1.0/serviceRate)
        serviceTimeDistribution.random_state = np.random.RandomState(seed=seed+i*2+45567)

    else:
        serviceTimeDistribution = None

    addServer(at=0.0, serviceTimeDistribution=serviceTimeDistribution)


# A maximum amount of simultaneous running processes is set as a fail safe, the processing stack for PS will otherwise
# quickly get overloaded if the system is unstable. Setting newMC=1 will result in a fcfs queueing discipline.
changeMC(at=0.0, newMC=10000)

# The arrival rate is set to a fraction of the service rate per server.
setRate(at = 0, rate = arrivalRateFrac*serviceRate*nbrServers)

# The simulation time is set to roughly match a certain amount of processed requests.
endOfSimulation(at = 1000/(arrivalRateFrac*nbrServers))
