import os
import numpy as np
from multiprocessing import Pool

# Parameters
MC_SIMS = range(0, 5)
SERVERS = range(1, 13)
LAMBDA_FRAC = np.arange(0.05, 0.71, 0.01)
PROCESSES = 24

# Add simulation commands as strings
simulations = []

max_frac = [0.7000, 0.7000, 0.7000, 0.6800, 0.6300, 0.5900, 0.5400, 0.5000, 0.4600, 0.4300, 0.4000, 0.3700]
buffer = 0.01

count = 0
for k in MC_SIMS:
    for servers in SERVERS:
        for i, frac in enumerate(LAMBDA_FRAC):

            if frac > max_frac[servers-1] + buffer:
                continue

            count += 1
            simulations.append("./simulator.py  --lb clone-random --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
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
