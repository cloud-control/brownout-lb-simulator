speedfactor = 0.35
addServer(y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(y = speedfactor * 0.07 * 2.0, n = speedfactor * 0.001 * 2.0)
addServer(y = speedfactor * 0.07 * 4.0, n = speedfactor * 0.001 * 4.0)

setRate(at =    0, rate = 200.0)

endOfSimulation(at = 500)
