# This scenario was constructed so that an ideal load balancer should be
# able to serve all requests optional content with a mean response time
# of T=1.

addServer(y = 0.07     , n = 0.001     )
addServer(y = 0.07 *  2, n = 0.001 *  2)
addServer(y = 0.07 *  3, n = 0.001 *  3)
addServer(y = 0.07 * 10, n = 0.001 * 50)
addServer(y = 0.07 * 10, n = 0.001 * 50)

global clients, lam

# Calculate the sum of 1 / (theta / mu + (1 - theta) / M) - 1 / Tref for
# all servers.
lam = 0
theta = 1
Tref = 1
for server in servers:
	lam += 1 / (theta*server.serviceTimeY + (theta-1)*server.serviceTimeN) - 1/Tref

clients = OpenLoopClient(sim, loadBalancer, rate=lam)

sim.add(1000, lambda: clients.setRate(lam/2))
sim.add(2000, lambda: clients.setRate(lam))
sim.add(4000, lambda: clients.setRate(lam/2))
sim.add(7000, lambda: clients.setRate(lam))

endOfSimulation(at = 10000)
