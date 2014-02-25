# Same as A, but service time of server 0 changes at 3000s

addServer(y = 0.07     , n = 0.001     )
addServer(y = 0.07 *  2, n = 0.001 *  2)
addServer(y = 0.07 *  3, n = 0.001 *  3)
addServer(y = 0.07 * 10, n = 0.001 * 50)
addServer(y = 0.07 * 10, n = 0.001 * 50)

addClients(at =    0, n = 50)
addClients(at = 1000, n = 50)
delClients(at = 2000, n = 75)
changeServiceTime(at = 3000, serverId = 0, y = 0.21, n = 0.003)
addClients(at = 4000, n = 25)

endOfSimulation(at = 5000)
