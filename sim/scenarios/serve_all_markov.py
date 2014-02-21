# This scenario was constructed so that an ideal load balancer should be
# able to serve all requests optional content with a mean response time
# of T=1.

addServer(y = 0.07     , n = 0.001     )
addServer(y = 0.07 *  2, n = 0.001 *  2)
addServer(y = 0.07 *  3, n = 0.001 *  3)
addServer(y = 0.07 * 10, n = 0.001 * 50)
addServer(y = 0.07 * 10, n = 0.001 * 50)

global clients, lam

lam = 22.8571428571

clients = MarkovianArrivalProcess(sim,loadBalancer,rate=lam)

sim.add(1000, lambda: clients.setRate(lam/2))
sim.add(2000, lambda: clients.setRate(lam))
sim.add(4000, lambda: clients.setRate(lam/2))
sim.add(7000, lambda: clients.setRate(lam))

endOfSimulation(at = 10000)
