speedfactor = 1.0
addServer(at=0.0,y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(at=0.0,y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(at=0.0,y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(at=0.0,y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(at=0.0,y = speedfactor * 0.07    , n = speedfactor * 0.001    )

for i in range(0, 21):
    setRate(at =    0+i*250, rate = 100.0)
    setRate(at =    50+i*250, rate = 500.0)
    setRate(at=100 + i * 250, rate=150.0)
    setRate(at=150 + i * 250, rate=350.0)
    setRate(at=200 + i * 250, rate=100.0)


endOfSimulation(at = 5250)
