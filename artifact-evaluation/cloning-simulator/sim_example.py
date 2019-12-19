import os
import numpy as np
from multiprocessing import Pool

# Parameters
PROCESSES = 10
MC_SIMS = range(0, 5)

# Simulation commands are added as strings to a list, which is later executed in parallel fashion.
simulations = []
count = 0
for k in MC_SIMS:
        count += 1
        simulations.append("./simulator.py  --lb clone-random --scenario scenarios/clone-example.py --cloning 1 --nbrClones 3 \
            --printout 0 --printRespTime 1 --dist SXmodel --serviceRate 1.0 --uniformArrivals 1 --arrivalRateFrac 0.5 --nbrOfServers 9 \
            --setSeed {} --outdir result_example/random/sim{}".format(count*10 + 123456, k))

        simulations.append("./simulator.py  --lb clone-SQF --scenario scenarios/clone-example.py --cloning 1 --nbrClones 3 \
            --printout 0 --printRespTime 1 --dist SXmodel --serviceRate 1.0 --uniformArrivals 1 --arrivalRateFrac 0.5 --nbrOfServers 9 \
            --setSeed {} --outdir result_example/sqf/sim{}".format(count*10 + 123456, k))


# Each simulation can take a while to execute, but runs in a single core. Since they are independent, parallel
# processing will speed up the process linearly with the amount of process up to the available number of cores on the
# machine.
pool = Pool(processes=PROCESSES)
for k, simulation in enumerate(simulations):
    simulation += " --printsim {}".format(k+1)
    pool.apply_async(os.system, (simulation,))

pool.close()
pool.join()
print "All simulations completed"
