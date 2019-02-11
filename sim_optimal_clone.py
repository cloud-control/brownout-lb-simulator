import os
import numpy as np
from multiprocessing import Pool

# Parameters
MC_SIMS = 5
SERVERS = range(1, 13)
LAMBDA_FRAC = np.arange(0.05, 0.96, 0.01)
PROCESSES = 24

# Add simulation commands as strings
simulations = []

count = 0
for k in range(MC_SIMS):
    for servers in SERVERS:
        for i, frac in enumerate(LAMBDA_FRAC):
            if frac > 0.7 and servers > 5:
                continue
            else:
                count += 1
                simulations.append("./simulator.py  --lb random --scenario scenarios/clone-sim_optimal_clone.py --cloning 1 --nbrClones {} \
                    --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers {} \
                    --setSeed {} --outdir result/s{}_af{}/sim{}".format(servers, frac, servers, count*10 + 123456, servers, i, k))

# Run the simulation
pool = Pool(processes=PROCESSES)
for k, simulation in enumerate(simulations):
    simulation += " --printsim {}".format(k+1)
    pool.apply_async(os.system, (simulation,))

pool.close()
pool.join()
print "All simulations completed"
