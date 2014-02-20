# This scenario was constructed so that an ideal load balancer should be
# able to serve all requests optional content with a response time T=1.

addServer(y = 0.07     , n = 0.001     )
addServer(y = 0.07 *  2, n = 0.001 *  2)
addServer(y = 0.07 *  3, n = 0.001 *  3)
addServer(y = 0.07 * 10, n = 0.001 * 50)
addServer(y = 0.07 * 10, n = 0.001 * 50)

lam = 22.8571428571

sim.markovClients = MarkovianArrivalProcess(sim,loadBalancer,rate=lam)

setRate(10000, lam/2)
setRate(20000, lam)
setRate(40000, lam/2)
setRate(70000, lam)

endOfSimulation(at = 10000)
