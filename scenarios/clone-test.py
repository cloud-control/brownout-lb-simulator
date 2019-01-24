speedfactor1 = 1.0
speedfactor2 = 1.0
speedfactor3 = 1.0
#addServer(at=0.0, y = speedfactor1 * 0.00    , n = speedfactor1 * 2.0, seed=518    )

nbrServers = 12
for i in range(0, nbrServers):
    addServer(at=0.0, y = speedfactor1 * 0.00001    , n = speedfactor1 * 2.0, seed=1    )


#addServer(at=0.0, y = speedfactor * 0.01    , n = speedfactor * 0.001    )

setRate(at =    0, rate = 0.30*nbrServers)

endOfSimulation(at = 100000)
