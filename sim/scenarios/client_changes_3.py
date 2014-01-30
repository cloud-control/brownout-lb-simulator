# one fast replica
addServer(y = 0.05     , n = 0.005     )

# one slow replicas
addServer(y = 0.05 * 10, n = 0.005 * 5 )

# one super-slow replicas
addServer(y = 0.05 * 50, n = 0.005 * 10)
addServer(y = 0.05 * 50, n = 0.005 * 10)

addClients(at =    0, n = 10 )
delClients(at = 1000, n =  5 )
addClients(at = 2000, n = 10 )
addClients(at = 3000, n =  5 )
delClients(at = 4000, n = 15 )
addClients(at = 5000, n = 10 )
delClients(at = 6000, n =  5 )
addClients(at = 7000, n = 20 )
delClients(at = 8000, n = 10 )
addClients(at = 9000, n =  5 )

endOfSimulation(at = 10000)
