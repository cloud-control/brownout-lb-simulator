speedfactor = 0.2
addServer(at=0.0,y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(at=0.0,y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(at=0.0,y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(at=0.0,y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(at=0.0,y = speedfactor * 0.07    , n = speedfactor * 0.001    )

nbrIterations = 21

changeMC(at=1.0, newMC=15)

for i in range(0, nbrIterations):
    setRate(at=0 + 150 * i, rate = 400.0)
    setRate(at =50   + 150*i, rate = 1500.0)
    setRate(at=100 + 150 * i, rate=400.0)


endOfSimulation(at = 150*nbrIterations)