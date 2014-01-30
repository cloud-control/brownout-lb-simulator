# four fast replicas
addServer(y = 0.05     , n = 0.005     )
addServer(y = 0.05     , n = 0.005     )
addServer(y = 0.05     , n = 0.005     )
addServer(y = 0.05     , n = 0.005     )

# four slow replicas
addServer(y = 0.05 * 10, n = 0.005 * 5 )
addServer(y = 0.05 * 10, n = 0.005 * 5 )
addServer(y = 0.05 * 10, n = 0.005 * 5 )
addServer(y = 0.05 * 10, n = 0.005 * 5 )

# two super-slow replicas
addServer(y = 0.05 * 50, n = 0.005 * 10)
addServer(y = 0.05 * 50, n = 0.005 * 10)

addClients(at =    0, n = 50 )
delClients(at = 1000, n = 25 )
addClients(at = 2000, n = 50 )
addClients(at = 3000, n = 25 )
delClients(at = 4000, n = 75 )
addClients(at = 5000, n = 50 )
delClients(at = 6000, n = 25 )
addClients(at = 7000, n = 50 )
delClients(at = 8000, n = 50 )
addClients(at = 9000, n = 50 )

endOfSimulation(at = 10000)
