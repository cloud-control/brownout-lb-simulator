# Scenario that we have been using almost since the beginning

addServer(y = 0.07     , n = 0.001     )
addServer(y = 0.07 *  2, n = 0.001 *  2)
addServer(y = 0.07 *  3, n = 0.001 *  3)
addServer(y = 0.07 * 10, n = 0.001 * 50)
addServer(y = 0.07 * 10, n = 0.001 * 50)

global markovClients

markovClients = MarkovianArrivalProcess(sim,loadBalancer,rate=30)

sim.add(1000, lambda: markovClients.setRate(60))
sim.add(2000, lambda: markovClients.setRate(40))
sim.add(4000, lambda: markovClients.setRate(80))

changeServiceTime(at = 250, serverId = 0, y = 0.07 * 5,  n = 0.001 * 5)
changeServiceTime(at = 500, serverId = 4, y = 0.07 * 1,  n = 0.001 * 1)
changeServiceTime(at = 750, serverId = 3, y = 0.07 * 1,  n = 0.001 * 1)

endOfSimulation(at = 5000)
