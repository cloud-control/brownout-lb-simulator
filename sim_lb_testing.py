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
arrivalDelayFracs = [0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5]

PROCESSES = 2
MAXRUNTIME = 20000

# Add simulation commands as strings
simulations = []

count = 0
for scenario in NBR_SCENARIOS:

    #dist = rnd.choice(dists)
    dist = "SXmodel"
    #util = rnd.choice(utils)
    util = 0.8
    #nbrServer = rnd.choice(nbrServers)
    nbrServer = 12
    cloneFactor = 4
    frac = getLambdaFrac(dist, util, cloneFactor)
    arrivalDelayFrac = rnd.choice(arrivalDelayFracs)
    meanServiceTime = getMeanServiceTime(dist, cloneFactor)
    #arrivalDelay = arrivalDelayFrac*meanServiceTime
    arrivalDelay = 0.0
    cancellationDelay = 0.0

    """print("-------------------")
    print(dist)
    print("util: " + str(util))
    print("nbrServer: " + str(nbrServer))
    print("cloneFactor: " + str(cloneFactor))
    print("lambda frac: " + str(frac))
    print("arrival delay frac: " + str(arrivalDelayFrac))
    print("arrival delay: " + str(arrivalDelay))
    print("-------------------")"""

    os.makedirs("result/lb_testing/scenario{}".format(scenario))

    count += 1
    simulations.append("./simulator.py  --lb clone-SQF --scenario scenarios/clone-PS-randomized.py --cloning 1 --nbrClones {} \
        --printout 0 --printRespTime 0 --arrivalDelay {} --cancellationDelay {} --dist {} --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers {} \
        --setSeed {} --maxRunTime {} --outdir result/lb_testing/scenario{}/SQF \
        ".format(cloneFactor, arrivalDelay, cancellationDelay, dist, frac, nbrServer, count*100 + 123456, MAXRUNTIME, scenario))

    count += 1
    simulations.append("./simulator.py  --lb clone-random --scenario scenarios/clone-PS-randomized.py --cloning 1 --nbrClones {} \
        --printout 0 --printRespTime 0 --arrivalDelay {} --cancellationDelay {} --dist {} --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers {} \
        --setSeed {} --maxRunTime {} --outdir result/lb_testing/scenario{}/random \
        ".format(cloneFactor, arrivalDelay, cancellationDelay, dist, frac, nbrServer, count*100 + 123456, MAXRUNTIME, scenario))

    count += 1
    simulations.append("./simulator.py  --lb cluster-SQF --scenario scenarios/clone-PS-randomized.py --cloning 1 --nbrClones {} \
        --printout 0 --printRespTime 0 --arrivalDelay {} --cancellationDelay {} --dist {} --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers {} \
        --setSeed {} --maxRunTime {} --outdir result/lb_testing/scenario{}/cluster_SQF \
        ".format(cloneFactor, arrivalDelay, cancellationDelay, dist, frac, nbrServer, count*100 + 123456, MAXRUNTIME, scenario))

    count += 1
    simulations.append("./simulator.py  --lb cluster-random --scenario scenarios/clone-PS-randomized.py --cloning 1 --nbrClones {} \
        --printout 0 --printRespTime 0 --arrivalDelay {} --cancellationDelay {} --dist {} --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers {} \
        --setSeed {} --maxRunTime {} --outdir result/lb_testing/scenario{}/cluster_random \
        ".format(cloneFactor, arrivalDelay, cancellationDelay, dist, frac, nbrServer, count*100 + 123456, MAXRUNTIME, scenario))

    with open("result/lb_testing/scenario{}/description.csv".format(scenario), 'a') as f:
        f.write("dist,{}\nutil,{}\nnbrServer,{}\ncloneFactor,{}\nmeanServiceTime,{}\nlambdafrac,{}\narrivalDelay,{}\ncancellationDelay,{}"
                .format(dist, util, nbrServer, cloneFactor, meanServiceTime, frac, arrivalDelay, cancellationDelay))


# Run the simulation
pool = Pool(processes=PROCESSES)
for k, simulation in enumerate(simulations):
    simulation += " --printsim {}".format(k+1)
    pool.apply_async(os.system, (simulation,))

pool.close()
pool.join()
print "All simulations completed"
