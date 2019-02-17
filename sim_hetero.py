import os
import numpy as np
from multiprocessing import Pool

# Parameters
MC_SIMS = range(0, 20)
LAMBDA_FRAC = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
PROCESSES = 24
MAXRUNTIME = 2000

# Add simulation commands as strings
simulations = []

count = 0
for sim in MC_SIMS:
    for i, frac in enumerate(LAMBDA_FRAC):
        count += 1
        simulations.append("./simulator.py  --lb cluster-w-random --scenario scenarios/clone-hetero-1122.py --cloning 1 --nbrClones 2  \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 4 \
            --setSeed {} --maxRunTime {} --outdir result/CWR-1122/af{}/sim{}".format(frac, count*20 + 21343213, MAXRUNTIME, i, sim))

        count += 1
        simulations.append("./simulator.py  --lb cluster-w-random --scenario scenarios/clone-hetero-1212.py --cloning 1 --nbrClones 2  \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 4 \
            --setSeed {} --maxRunTime {}  --outdir result/CWR-1212/af{}/sim{}".format(frac, count*20 + 21343213, MAXRUNTIME, i, sim))

        count += 1
        simulations.append("./simulator.py  --lb cluster-w-random --scenario scenarios/clone-hetero-1212.py --cloning 1 --nbrClones 4  \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 4 \
            --setSeed {} --maxRunTime {}  --outdir result/CWR-all/af{}/sim{}".format(frac, count*20 + 21343213, MAXRUNTIME, i, sim))

        count += 1
        simulations.append("./simulator.py  --lb cluster-w-random --scenario scenarios/clone-hetero-1212.py --cloning 1 --nbrClones 1  \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 4 \
            --setSeed {} --maxRunTime {}  --outdir result/CWR-none/af{}/sim{}".format(frac, count*20 + 21343213, MAXRUNTIME, i, sim))

        count += 1
        simulations.append("./simulator.py  --lb cluster-SED --scenario scenarios/clone-hetero-1122.py --cloning 1 --nbrClones 2  \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 4 \
            --setSeed {} --maxRunTime {}  --outdir result/SED-1122/af{}/sim{}".format(frac, count*20 + 21343213, MAXRUNTIME, i, sim))

        count += 1
        simulations.append("./simulator.py  --lb cluster-SED --scenario scenarios/clone-hetero-1212.py --cloning 1 --nbrClones 2  \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 4 \
            --setSeed {} --maxRunTime {}  --outdir result/SED-1212/af{}/sim{}".format(frac, count*20 + 21343213, MAXRUNTIME, i, sim))

        count += 1
        simulations.append("./simulator.py  --lb cluster-SED --scenario scenarios/clone-hetero-1212.py --cloning 1 --nbrClones 4  \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 4 \
            --setSeed {} --maxRunTime {}  --outdir result/SED-all/af{}/sim{}".format(frac, count*20 + 21343213, MAXRUNTIME, i, sim))

        count += 1
        simulations.append("./simulator.py  --lb cluster-SED --scenario scenarios/clone-hetero-1212.py --cloning 1 --nbrClones 1  \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 4 \
            --setSeed {} --maxRunTime {}  --outdir result/SED-none/af{}/sim{}".format(frac, count*20 + 21343213, MAXRUNTIME, i, sim))

# Run the simulation
pool = Pool(processes=PROCESSES)
for k, simulation in enumerate(simulations):
    simulation += " --printsim {}".format(k+1)
    pool.apply_async(os.system, (simulation,))

pool.close()
pool.join()
print "All simulations completed"
