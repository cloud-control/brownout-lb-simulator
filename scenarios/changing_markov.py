# Scenario that we have been using almost since the beginning

addServer(y = 0.07     , n = 0.001     )
addServer(y = 0.07 *  2, n = 0.001 *  2)
addServer(y = 0.07 *  3, n = 0.001 *  3)
addServer(y = 0.07 * 10, n = 0.001 * 50)
addServer(y = 0.07 * 10, n = 0.001 * 50)

setRate(at =    0, rate = 30)
setRate(at = 1000, rate = 60)
setRate(at = 2000, rate = 40)
setRate(at = 4000, rate = 80)

endOfSimulation(at = 5000)
