import random as xxx_random # prevent accidental usage
from base.utils import *


scen_min = 0
scen_max = 1
seed_input = 222454


rnd = xxx_random.Random()
rnd.seed(seed_input)

# Parameters
NBR_SCENARIOS = range(scen_min, scen_max)

dists = ["SXmodel", "expon", "pareto", "uniform", "weibull_min"]
utils = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
nbrServers = [4, 6, 9, 12, 15, 21, 27, 30, 45, 48]

MAXRUNTIME = 10000

def getRandomCloneFactor(nbrServers):
    cloneFactors = []
    for nbr in range(2, nbrServers):
        if nbrServers % nbr == 0:
            cloneFactors.append(nbr)

    return rnd.choice(cloneFactors)

count = 0
for scenario in NBR_SCENARIOS:

    dist = rnd.choice(dists)
    util = rnd.choice(utils)
    nbrServer = rnd.choice(nbrServers)
    cloneFactor = getRandomCloneFactor(nbrServer)
    frac = getLambdaFrac(dist, util, cloneFactor)

    count += 1
    print("./simulator.py  --lb cluster-SQF --scenario scenarios/clone-PS-randomized.py --cloning 1 --nbrClones {} \
        --printout 1 --printRespTime 0 --dist {} --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers {} \
        --setSeed {} --maxRunTime {} --outdir result/randomized_sync_vs_nonsync/scenario{}/clusterSQF-PS \
        ".format(cloneFactor, dist, frac, nbrServer, count*100 + 123456, MAXRUNTIME, scenario))

    count += 1
    print("./simulator.py  --lb cluster-random --scenario scenarios/clone-PS-randomized.py --cloning 1 --nbrClones {} \
        --printout 1 --printRespTime 0 --dist {} --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers {} \
        --setSeed {} --maxRunTime {} --outdir result/randomized_sync_vs_nonsync/scenario{}/clusterRandom-PS \
        ".format(cloneFactor, dist, frac, nbrServer, count*100 + 123456, MAXRUNTIME, scenario))

    count += 1
    print("./simulator.py  --lb clone-SQF --scenario scenarios/clone-PS-randomized.py --cloning 1 --nbrClones {} \
        --printout 1 --printRespTime 0 --dist {} --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers {} \
        --setSeed {} --maxRunTime {} --outdir result/randomized_sync_vs_nonsync/scenario{}/SQF-PS \
        ".format(cloneFactor, dist, frac, nbrServer, count*100 + 123456, MAXRUNTIME, scenario))

    count += 1
    print("./simulator.py  --lb clone-random --scenario scenarios/clone-PS-randomized.py --cloning 1 --nbrClones {} \
        --printout 1 --printRespTime 0 --dist {} --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers {} \
        --setSeed {} --maxRunTime {} --outdir result/randomized_sync_vs_nonsync/scenario{}/Random-PS \
        ".format(cloneFactor, dist, frac, nbrServer, count*100 + 123456, MAXRUNTIME, scenario))
