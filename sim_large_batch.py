import os
import numpy as np
from multiprocessing import Pool

# Parameters
MC_SIMS = range(0, 20)
LAMBDA_FRAC = [0.1, 0.3, 0.5, 0.7]
CLONES = [1, 2, 3, 4, 6, 12]
PROCESSES = 24
MAXRUNTIME = 2000

# Add simulation commands as strings
simulations = []

count = 0
for sim in MC_SIMS:
    for i, frac in enumerate(LAMBDA_FRAC):
        count += 1
        simulations.append("./simulator.py  --lb IQ-12 --scenario scenarios/clone-FCFS.py --cloning 1 --nbrClones 1 \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
            --setSeed {} --maxRunTime {} --outdir result/IQ12/af{}/sim{}".format(frac, count*10 + 123456, MAXRUNTIME, i, sim))

        count += 1
        simulations.append("./simulator.py  --lb RIQ-12 --scenario scenarios/clone-FCFS.py --cloning 1 --nbrClones 1 \
            --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
            --setSeed {} --maxRunTime {} --outdir result/RIQ12/af{}/sim{}".format(frac, count*10 + 123456, MAXRUNTIME, i, sim))

        for clones in CLONES:
            ###
            count += 1
            simulations.append("./simulator.py  --lb cluster-SQF --scenario scenarios/clone-FCFS.py --cloning 1 --nbrClones {} \
                --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
                --setSeed {} --maxRunTime {} --outdir result/clusterSQF-FCFS/c{}_af{}/sim{} \
                ".format(clones, frac, count*10 + 123456, MAXRUNTIME, clones, i, sim))

            count += 1
            simulations.append("./simulator.py  --lb cluster-SQF --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
                --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
                --setSeed {} --maxRunTime {} --outdir result/clusterSQF-PS/c{}_af{}/sim{} \
                ".format(clones, frac, count*10 + 123456, MAXRUNTIME, clones, i, sim))

            count += 1
            simulations.append("./simulator.py  --lb cluster-random --scenario scenarios/clone-FCFS.py --cloning 1 --nbrClones {} \
                --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
                --setSeed {} --maxRunTime {} --outdir result/clusterRandom-FCFS/c{}_af{}/sim{} \
                ".format(clones, frac, count*10 + 123456, MAXRUNTIME, clones, i, sim))

            count += 1
            simulations.append("./simulator.py  --lb cluster-random --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
                --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
                --setSeed {} --maxRunTime {} --outdir result/clusterRandom-PS/c{}_af{}/sim{} \
                ".format(clones, frac, count*10 + 123456, MAXRUNTIME, clones, i, sim))

            ###
            count += 1
            simulations.append("./simulator.py  --lb clone-SQF --scenario scenarios/clone-FCFS.py --cloning 1 --nbrClones {} \
                --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
                --setSeed {} --maxRunTime {} --outdir result/SQF-FCFS/c{}_af{}/sim{} \
                ".format(clones, frac, count*10 + 123456, MAXRUNTIME, clones, i, sim))

            count += 1
            simulations.append("./simulator.py  --lb clone-SQF --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
                --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
                --setSeed {} --maxRunTime {} --outdir result/SQF-PS/c{}_af{}/sim{} \
                ".format(clones, frac, count*10 + 123456, MAXRUNTIME, clones, i, sim))

            count += 1
            simulations.append("./simulator.py  --lb clone-random --scenario scenarios/clone-FCFS.py --cloning 1 --nbrClones {} \
                --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
                --setSeed {} --maxRunTime {} --outdir result/Random-FCFS/c{}_af{}/sim{} \
                ".format(clones, frac, count*10 + 123456, MAXRUNTIME, clones, i, sim))

            count += 1
            simulations.append("./simulator.py  --lb clone-random --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
                --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
                --setSeed {} --maxRunTime {} --outdir result/Random-PS/c{}_af{}/sim{} \
                ".format(clones, frac, count*10 + 123456, MAXRUNTIME, clones, i, sim))

            count += 1
            simulations.append("./simulator.py  --lb RR --scenario scenarios/clone-FCFS.py --cloning 1 --nbrClones {} \
                --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
                --setSeed {} --maxRunTime {} --outdir result/RR-FCFS/c{}_af{}/sim{} \
                ".format(clones, frac, count*10 + 123456, MAXRUNTIME, clones, i, sim))

            count += 1
            simulations.append("./simulator.py  --lb RR --scenario scenarios/clone-PS.py --cloning 1 --nbrClones {} \
                --printout 0 --printRespTime 0 --dist SXmodel --serviceRate 1.0 --arrivalRateFrac {} --nbrOfServers 12 \
                --setSeed {} --maxRunTime {} --outdir result/RR-PS/c{}_af{}/sim{} \
                ".format(clones, frac, count*10 + 123456, MAXRUNTIME, clones, i, sim))




# Run the simulation
pool = Pool(processes=PROCESSES)
for k, simulation in enumerate(simulations):
    simulation += " --printsim {}".format(k+1)
    pool.apply_async(os.system, (simulation,))

pool.close()
pool.join()
print "All simulations completed"
