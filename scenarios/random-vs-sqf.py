speedfactor = 0.2
addServer(at=0.0,y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(at=0.0,y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(at=0.0,y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(at=0.0,y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(at=0.0,y = speedfactor * 0.07    , n = speedfactor * 0.001    )

nbrIterations = 21

for i in range(0, nbrIterations):
    setRate(at=0 + 100 * i, rate = 400.0)
    changeMC(at=1.0, newMC=15)
    setRate(at =50   + 100*i, rate = 1500.0)


endOfSimulation(at = 100*nbrIterations)