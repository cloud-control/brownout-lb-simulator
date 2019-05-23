import os
import numpy as np
from multiprocessing import Pool

# Parameters
MC_SIMS = range(0, 20)
LAMBDA_FRAC = np.arange(0.1, 0.75, 0.05) #[0.1, 0.2 0.3, 0.5, 0.7]
CLONES = [2, 3, 4, 6]
PROCESSES = 24
MAXRUNTIME = 1000

# Add simulation commands as strings
simulations = []

buffer = 0.01 # Because of greater than
count = 0
for sim in MC_SIMS:
    for i, frac in enumerate(LAMBDA_FRAC):

        for clones in CLONES:
            ###

            if not ((clones == 6 and frac > 0.55+buffer) or (clones == 4 and frac > 0.65+buffer)):
                count += 1
                simulations.append("./simulator.py  --lb cluster-SQF --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
                    --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
                    --setSeed {} --maxRunTime {} --outdir result/clusterSQF-PS-dolly/c{}_af{}/sim{} \
                    ".format(clones, frac, count*10 + 123456, MAXRUNTIME, clones, i, sim))

                count += 1
                simulations.append("./simulator.py  --lb clone-SQF --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
                    --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
                    --setSeed {} --maxRunTime {} --outdir result/SQF-PS-dolly/c{}_af{}/sim{} \
                    ".format(clones, frac, count*10 + 123456, MAXRUNTIME, clones, i, sim))



# Run the simulation
pool = Pool(processes=PROCESSES)
for k, simulation in enumerate(simulations):
    simulation += " --printsim {}".format(k+1)
    pool.apply_async(os.system, (simulation,))

pool.close()
pool.join()
print "All simulations completed"
