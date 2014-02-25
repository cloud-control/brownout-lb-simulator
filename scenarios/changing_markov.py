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

endOfSimulation(at = 5000)
