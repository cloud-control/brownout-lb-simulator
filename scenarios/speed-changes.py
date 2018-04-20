speedfactor = 1.0
addServer(at=0,y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(at=0,y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(at=0,y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(at=0,y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(at=0,y = speedfactor * 0.07    , n = speedfactor * 0.001    )

setRate(at =    0, rate = 500.0)

nbrIter = 21

for i in range(0, nbrIter):
    for id in range(0, 1):
        changeServiceTime(at=50 + i * 250, serverId=id, y=speedfactor * 2/3* 0.07, n=speedfactor * 2/3* 0.001)
        changeServiceTime(at=100 + i * 250, serverId=id, y=speedfactor * 1.5 * 0.07, n=speedfactor * 1.5 * 0.001)
        changeServiceTime(at=150 + i * 250, serverId=id, y=speedfactor * 2/3 * 0.07, n=speedfactor * 2/3* 0.001)
        changeServiceTime(at=200 + i * 250, serverId=id, y=speedfactor * 1.0 * 0.07, n=speedfactor * 1.0 * 0.001)


endOfSimulation(at = nbrIter*250.0)
