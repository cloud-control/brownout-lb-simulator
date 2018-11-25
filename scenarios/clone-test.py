speedfactor1 = 2
speedfactor2 = 1
speedfactor3 = 0.666666
addServer(at=0.0, y = speedfactor1 * 0.01    , n = speedfactor1 * 0.001    )
addServer(at=0.0, y = speedfactor2 * 0.01    , n = speedfactor2 * 0.001    )
addServer(at=0.0, y = speedfactor3 * 0.01    , n = speedfactor3 * 0.001    )
#addServer(at=0.0, y = speedfactor * 0.01    , n = speedfactor * 0.001    )

setRate(at =    0, rate = 200.0)

endOfSimulation(at = 1000)
