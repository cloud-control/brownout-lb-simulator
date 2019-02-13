import os
import numpy as np
from multiprocessing import Pool

# Parameters
MC_SIMS = range(0, 20)
LAMBDA_FRAC = [0.1, 0.3, 0.5, 0.7]
CLONES = [1, 2, 3, 4, 6, 12]
PROCESSES = 4

# Add simulation commands as strings
simulations = []

count = 0
for sim in MC_SIMS:
    for clones in CLONES:
        for i, frac in enumerate(LAMBDA_FRAC):
            count += 1
            simulations.append("./simulator.py  --lb central-queue --scenario scenarios/clone-central_queue.py --cloning 1 --nbrClones {} \
                --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
                --setSeed {} --outdir result/c{}_af{}/sim{}".format(clones, frac, count*10 + 123456, clones, i, sim))

# Run the simulation
pool = Pool(processes=PROCESSES)
for k, simulation in enumerate(simulations):
    simulation += " --printsim {}".format(k+1)
    pool.apply_async(os.system, (simulation,))

pool.close()
pool.join()
print "All simulations completed"
