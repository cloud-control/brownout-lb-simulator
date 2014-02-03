# Same as A, but service time of server 0 changes at 3000s

addServer(y = 0.07     , n = 0.001     )
addServer(y = 0.07 *  2, n = 0.001 *  2)
addServer(y = 0.07 *  2, n = 0.001 *  2)
addServer(y = 0.07 * 10, n = 0.001 * 10)
addServer(y = 0.07 * 10, n = 0.001 * 10)

addClients(at =    0, n = 100)

changeServiceTime(at = 200, serverId = 0, y = 0.07 * 10, n = 0.001 * 10)
changeServiceTime(at = 400, serverId = 4, y = 0.07 * 2,  n = 0.001 * 2)
changeServiceTime(at = 600, serverId = 0, y = 0.07 * 2,  n = 0.001 * 2)
changeServiceTime(at = 800, serverId = 0, y = 0.07 * 1,  n = 0.001 * 1)

endOfSimulation(at = 5000)