import os
import numpy as np
from multiprocessing import Pool

# Parameters
MC_SIMS = range(0, 20)
LAMBDA_FRAC_2 = [0.1000, 0.3000, 0.5000, 0.7000, 0.9000]
LAMBDA_FRAC_4 = [0.1000, 0.3000, 0.5000, 0.7000, 0.9000]

PROCESSES = 24
MAXRUNTIME = 5000

# Add simulation commands as strings
simulations = []

count = 0
for sim in MC_SIMS:
    for i, frac in enumerate(LAMBDA_FRAC_2):

        count += 1
        simulations.append("./simulator.py  --lb cluster-SQF --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
            --setSeed {} --maxRunTime {} --outdir result/sync_vs_nonsync_exponential/clusterSQF-PS/c{}_af{}/sim{} \
            ".format(2, frac, count*100 + 123456, MAXRUNTIME, 2, i, sim))

        count += 1
        simulations.append("./simulator.py  --lb cluster-random --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
            --setSeed {} --maxRunTime {} --outdir result/sync_vs_nonsync_exponential/clusterRandom-PS/c{}_af{}/sim{} \
            ".format(2, frac, count*100 + 123456, MAXRUNTIME, 2, i, sim))

        count += 1
        simulations.append("./simulator.py  --lb clone-SQF --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
            --setSeed {} --maxRunTime {} --outdir result/sync_vs_nonsync_exponential/SQF-PS/c{}_af{}/sim{} \
            ".format(2, frac, count*100 + 123456, MAXRUNTIME, 2, i, sim))

        count += 1
        simulations.append("./simulator.py  --lb clone-random --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
            --setSeed {} --maxRunTime {} --outdir result/sync_vs_nonsync_exponential/Random-PS/c{}_af{}/sim{} \
            ".format(2, frac, count*100 + 123456, MAXRUNTIME, 2, i, sim))


count = 500
for sim in MC_SIMS:
    for i, frac in enumerate(LAMBDA_FRAC_4):

        count += 1
        simulations.append("./simulator.py  --lb cluster-SQF --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
            --setSeed {} --maxRunTime {} --outdir result/sync_vs_nonsync_exponential/clusterSQF-PS/c{}_af{}/sim{} \
            ".format(4, frac, count*100 + 123456, MAXRUNTIME, 4, i, sim))

        count += 1
        simulations.append("./simulator.py  --lb cluster-random --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
            --setSeed {} --maxRunTime {} --outdir result/sync_vs_nonsync_exponential/clusterRandom-PS/c{}_af{}/sim{} \
            ".format(4, frac, count*100 + 123456, MAXRUNTIME, 4, i, sim))

        count += 1
        simulations.append("./simulator.py  --lb clone-SQF --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
            --setSeed {} --maxRunTime {} --outdir result/sync_vs_nonsync_exponential/SQF-PS/c{}_af{}/sim{} \
            ".format(4, frac, count*100 + 123456, MAXRUNTIME, 4, i, sim))

        count += 1
        simulations.append("./simulator.py  --lb clone-random --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
            --setSeed {} --maxRunTime {} --outdir result/sync_vs_nonsync_exponential/Random-PS/c{}_af{}/sim{} \
            ".format(4, frac, count*100 + 123456, MAXRUNTIME, 4, i, sim))




# Run the simulation
pool = Pool(processes=PROCESSES)
for k, simulation in enumerate(simulations):
    simulation += " --printsim {}".format(k+1)
    pool.apply_async(os.system, (simulation,))

pool.close()
pool.join()
print "All simulations completed"
