import os
import numpy as np
from multiprocessing import Pool

# Parameters
SIMS = 10
PROCESSES = 4

# Add simulation commands as strings
simulations = []

arrival_rates = np.linspace(0.1, 0.9, SIMS)
for k in range(SIMS):
    simulations.append("./simulator.py  --lb SQF --scenario scenarios/clone-test-FCFS.py --cloning 1 --nbrClones 1 \
        --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
        --maxRunTime 30 --outdir result/test/run{}".format(arrival_rates[k], k))

# Run the simulation
pool = Pool(processes=PROCESSES)
for k, simulation in enumerate(simulations):
    simulation += " --printsim {}".format(k+1)
    pool.apply_async(os.system, (simulation,))

pool.close()
pool.join()
print "All simulations completed"
