import os
import numpy as np
from multiprocessing import Pool

# Parameters
MC_SIMS = range(0, 20)
LAMBDA_FRAC_2 = [0.0799, 0.2396, 0.3993, 0.5590, 0.7187]
LAMBDA_FRAC_4 = [0.0685, 0.2055, 0.3425, 0.4795, 0.6165]

PROCESSES = 24
MAXRUNTIME = 2000

# Add simulation commands as strings
simulations = []

count = 0
for sim in MC_SIMS:
    for i, frac in enumerate(LAMBDA_FRAC_2):

        count += 1
        simulations.append("./simulator.py  --lb cluster-SQF --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
            --setSeed {} --maxRunTime {} --outdir result/sync_vs_nonsync/clusterSQF-PS/c{}_af{}/sim{} \
            ".format(2, frac, count*100 + 123456, MAXRUNTIME, 2, i, sim))

        count += 1
        simulations.append("./simulator.py  --lb cluster-random --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
            --setSeed {} --maxRunTime {} --outdir result/sync_vs_nonsync/clusterRandom-PS/c{}_af{}/sim{} \
            ".format(2, frac, count*100 + 123456, MAXRUNTIME, 2, i, sim))

        count += 1
        simulations.append("./simulator.py  --lb clone-SQF --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
            --setSeed {} --maxRunTime {} --outdir result/sync_vs_nonsync/SQF-PS/c{}_af{}/sim{} \
            ".format(2, frac, count*100 + 123456, MAXRUNTIME, 2, i, sim))

        count += 1
        simulations.append("./simulator.py  --lb clone-random --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
            --setSeed {} --maxRunTime {} --outdir result/sync_vs_nonsync/Random-PS/c{}_af{}/sim{} \
            ".format(2, frac, count*100 + 123456, MAXRUNTIME, 2, i, sim))


count = 500
for sim in MC_SIMS:
    for i, frac in enumerate(LAMBDA_FRAC_4):

        count += 1
        simulations.append("./simulator.py  --lb cluster-SQF --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
            --setSeed {} --maxRunTime {} --outdir result/sync_vs_nonsync/clusterSQF-PS/c{}_af{}/sim{} \
            ".format(4, frac, count*100 + 123456, MAXRUNTIME, 4, i, sim))

        count += 1
        simulations.append("./simulator.py  --lb cluster-random --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
            --setSeed {} --maxRunTime {} --outdir result/sync_vs_nonsync/clusterRandom-PS/c{}_af{}/sim{} \
            ".format(4, frac, count*100 + 123456, MAXRUNTIME, 4, i, sim))

        count += 1
        simulations.append("./simulator.py  --lb clone-SQF --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
            --setSeed {} --maxRunTime {} --outdir result/sync_vs_nonsync/SQF-PS/c{}_af{}/sim{} \
            ".format(4, frac, count*100 + 123456, MAXRUNTIME, 4, i, sim))

        count += 1
        simulations.append("./simulator.py  --lb clone-random --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
            --setSeed {} --maxRunTime {} --outdir result/sync_vs_nonsync/Random-PS/c{}_af{}/sim{} \
            ".format(4, frac, count*100 + 123456, MAXRUNTIME, 4, i, sim))




# Run the simulation
pool = Pool(processes=PROCESSES)
for k, simulation in enumerate(simulations):
    simulation += " --printsim {}".format(k+1)
    pool.apply_async(os.system, (simulation,))

pool.close()
pool.join()
print "All simulations completed"
