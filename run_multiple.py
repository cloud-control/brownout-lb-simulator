import os
from multiprocessing import Pool

# Parameters
PROCESSES = 4

# Add simulation commands as strings
simulations = []

for k in range(50):
    simulations.append("./simulator.py  --lb RIQ-d --scenario scenarios/clone-test.py --cloning 1 --nbrClones 1 \
        --printout 0 --outdir result/run{}".format(k))

# Run the simulations
pool = Pool(processes=PROCESSES)
for k, simulation in enumerate(simulations):
    simulation += " --printsim {}".format(k+1)
    pool.apply_async(os.system, (simulation,))

pool.close()
pool.join()
print "All simulations completed"
