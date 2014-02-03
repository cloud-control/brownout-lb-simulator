# one fast replica
addServer(y = 0.05     , n = 0.005     )

# one slow replicas
addServer(y = 0.05 * 5, n = 0.005 * 5 )

# two super-slow replicas
addServer(y = 0.05 * 10, n = 0.005 * 10)
addServer(y = 0.05 * 10, n = 0.005 * 10)

addClients(at =   0, n = 50 )
delClients(at = 200, n = 10 )
addClients(at = 400, n = 25 )
addClients(at = 600, n = 25 )
delClients(at = 800, n = 40 )

endOfSimulation(at = 1000)
