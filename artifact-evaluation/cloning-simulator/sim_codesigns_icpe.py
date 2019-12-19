import os
import numpy as np
from multiprocessing import Pool

# Parameters
MC_SIMS = range(0, 20)
LAMBDA_FRAC = [0.30, 0.38, 0.52, 0.62, 0.70]
CLONES = [1, 2, 3, 4, 6, 12]
PROCESSES = 24
MAXRUNTIME = 2000

# Add simulation commands as strings
simulations = []

max_frac = [0.7000, 0.7000, 0.62, 0.62, 0.52, 0.30]
buffer = 0.01

count = 0
for sim in MC_SIMS:
    for i, frac in enumerate(LAMBDA_FRAC):
        for k, clones in enumerate(CLONES):
            ###

            if frac > max_frac[k] + buffer:
                continue

            count += 1
            simulations.append("./simulator.py  --lb cluster-SQF --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
                --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
                --setSeed {} --maxRunTime {} --outdir result/clusterSQF-PS/c{}_af{}/sim{} \
                ".format(clones, frac, count*100 + 123456, MAXRUNTIME, clones, i, sim))

            count += 1
            simulations.append("./simulator.py  --lb cluster-random --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
                --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
                --setSeed {} --maxRunTime {} --outdir result/clusterRandom-PS/c{}_af{}/sim{} \
                ".format(clones, frac, count*100 + 123456, MAXRUNTIME, clones, i, sim))

# Run the simulation
pool = Pool(processes=PROCESSES)
for k, simulation in enumerate(simulations):
    simulation += " --printsim {}".format(k+1)
    pool.apply_async(os.system, (simulation,))

pool.close()
pool.join()
print "All simulations completed"