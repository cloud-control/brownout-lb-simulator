speedfactor = 1.0
addServer(y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(y = speedfactor * 0.07    , n = speedfactor * 0.001    )

setRate(at =    0, rate = 500.0)

for i in range(0, 2):
    for id in range(0, 5):
        changeServiceTime(at=50 + i * 250, serverId=id, y=speedfactor * 0.20 * 0.07, n=speedfactor * 0.20 * 0.001)
        changeServiceTime(at=100 + i * 250, serverId=id, y=speedfactor * 0.667 * 0.07, n=speedfactor * 0.667 * 0.001)
        changeServiceTime(at=150 + i * 250, serverId=id, y=speedfactor * 0.2857 * 0.07, n=speedfactor * 0.2857 * 0.001)
        changeServiceTime(at=200 + i * 250, serverId=id, y=speedfactor * 1.0 * 0.07, n=speedfactor * 1.0 * 0.001)


endOfSimulation(at = 500)
