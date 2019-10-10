import os
import sys
import numpy as np
from multiprocessing import Pool
import random as xxx_random # prevent accidental usage
from base.utils import *

if len(sys.argv) == 4:
    scen_min = int(sys.argv[1])
    scen_max = int(sys.argv[2])
    seed_input = int(sys.argv[3])
else:
    print("No input, setting to default")
    scen_min = 0
    scen_max = 1000
    seed_input = 222454


rnd = xxx_random.Random()
rnd.seed(seed_input)

# Parameters
NBR_SCENARIOS = range(scen_min, scen_max)

dists = ["SXmodel", "expon", "pareto", "uniform", "weibull_min"]
utils = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
nbrServers = [2, 3, 4, 5, 6, 7, 9, 10, 12, 15]
cancellationDelayFracs = [0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5]

PROCESSES = 24
MAXRUNTIME = 20000

# Add simulation commands as strings
simulations = []

def getRandomStableCancellationFrac(util):
    safeFracs = [x for x in cancellationDelayFracs if x+util < 1.0]
    print("safe fracs: " + str(safeFracs))
    return rnd.choice(safeFracs)

count = 0
for scenario in NBR_SCENARIOS:

    dist = rnd.choice(dists)
    util = rnd.choice(utils)
    nbrServer = rnd.choice(nbrServers)
    cloneFactor = nbrServer
    frac = getLambdaFrac(dist, util, cloneFactor)
    arrivalDelay = 0.0
    cancellationDelayFrac = getRandomStableCancellationFrac(util)
    meanServiceTime = getMeanServiceTime(dist, cloneFactor)
    cancellationDelay = cancellationDelayFrac*meanServiceTime

    """print("-------------------")
    print(dist)
    print("util: " + str(util))
    print("nbrServer: " + str(nbrServer))
    print("cloneFactor: " + str(cloneFactor))
    print("lambda frac: " + str(frac))
    print("cancellation delay frac: " + str(cancellationDelayFrac))
    print("cancellation delay: " + str(cancellationDelay))
    print("-------------------")"""

    os.makedirs("result/randomized_cancellation_delays/scenario{}".format(scenario))

    count += 1
    simulations.append("./simulator.py  --lb clone-random --scenario scenarios/clone-PS-randomized.py --cloning 1 --nbrClones {} \
        --printout 0 --printRespTime 0 --arrivalDelay {} --cancellationDelay {} --dist {} --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers {} \
        --setSeed {} --maxRunTime {} --outdir result/randomized_cancellation_delays/scenario{} \
        ".format(cloneFactor, arrivalDelay, cancellationDelay, dist, frac, nbrServer, count*100 + 123456, MAXRUNTIME, scenario))

    with open("result/randomized_cancellation_delays/scenario{}/description.csv".format(scenario), 'a') as f:
        f.write("dist,{}\nutil,{}\nnbrServer,{}\ncloneFactor,{}\nmeanServiceTime,{}\nlambdafrac,{}\narrivalDelay,{}\ncancellationDelayFrac,{}\ncancellationDelay,{}"
                .format(dist, util, nbrServer, cloneFactor, meanServiceTime, frac, arrivalDelay, cancellationDelayFrac, cancellationDelay))


# Run the simulation
pool = Pool(processes=PROCESSES)
for k, simulation in enumerate(simulations):
    simulation += " --printsim {}".format(k+1)
    pool.apply_async(os.system, (simulation,))

pool.close()
pool.join()
print "All simulations completed"
