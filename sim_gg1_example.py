import os
import numpy as np
from multiprocessing import Pool

# Parameters
MC_SIMS = range(0, 1)
PROCESSES = 2

# Add simulation commands as strings
simulations = []

count = 0
for k in MC_SIMS:
        count += 1
        simulations.append("./simulator.py  --lb clone-random --scenario scenarios/clone-gg1_3dist.py --cloning 1 --nbrClones 3 \
            --printout 0 --printRespTime 1 --dist SXmodel --serviceRate 1.0 --uniformArrivals 1 --arrivalRateFrac 0.5 --nbrOfServers 3 \
            --setSeed {} --outdir result_gg1Example/3dist/sim{}".format(count*10 + 123456, k))

        simulations.append("./simulator.py  --lb clone-random --scenario scenarios/clone-gg1_equivalent.py --cloning 1 --nbrClones 1 \
            --printout 0 --printRespTime 1 --dist fromPath --path dists/mintest-v2.csv  --serviceRate 1.0 --uniformArrivals 1 \
            --arrivalRateFrac 0.5 --nbrOfServers 1 --setSeed {} --outdir result_gg1Example/equivalent/sim{}".format(count*10 + 123456, k))

        simulations.append("./simulator.py  --lb clone-random --scenario scenarios/clone-gg1_3dist-ps.py --cloning 1 --nbrClones 3 \
            --printout 0 --printRespTime 1 --dist SXmodel --serviceRate 1.0 --uniformArrivals 1 --arrivalRateFrac 0.5 --nbrOfServers 3 \
            --setSeed {} --outdir result_gg1Example/3dist-ps/sim{}".format(count*10 + 123456, k))

        simulations.append("./simulator.py  --lb clone-random --scenario scenarios/clone-gg1_equivalent-ps.py --cloning 1 --nbrClones 1 \
            --printout 0 --printRespTime 1 --dist fromPath --path dists/mintest-v2.csv  --serviceRate 1.0 --uniformArrivals 1 \
            --arrivalRateFrac 0.5 --nbrOfServers 1 --setSeed {} --outdir result_gg1Example/equivalent-ps/sim{}".format(count*10 + 123456, k))

# Run the simulation
pool = Pool(processes=PROCESSES)
for k, simulation in enumerate(simulations):
    simulation += " --printsim {}".format(k+1)
    pool.apply_async(os.system, (simulation,))

pool.close()
pool.join()
print "All simulations completed"
