# Same as A, but service time of server 0 changes at 3000s

addServer(y = 0.07     , n = 0.001     )
addServer(y = 0.07 *  2, n = 0.001 *  2)
addServer(y = 0.07 *  2, n = 0.001 *  2)
addServer(y = 0.07 * 10, n = 0.001 * 10)
addServer(y = 0.07 * 10, n = 0.001 * 10)

addClients(at =    0, n = 50)

changeServiceTime(at = 250, serverId = 0, y = 0.07 * 5,  n = 0.001 * 5)
changeServiceTime(at = 500, serverId = 4, y = 0.07 * 1,  n = 0.001 * 1)
changeServiceTime(at = 750, serverId = 3, y = 0.07 * 1,  n = 0.001 * 1)

endOfSimulation(at = 1000)
