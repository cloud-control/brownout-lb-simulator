# Scenario to test autoscaling

addServer(y = 0.07     , n = 0.001     , autoScale = False) # ensure at least one server is connected
addServer(y = 0.07 *  2, n = 0.001 *  2, autoScale = True)
addServer(y = 0.07 *  3, n = 0.001 *  3, autoScale = True)
addServer(y = 0.07 * 10, n = 0.001 * 50, autoScale = True)
addServer(y = 0.07 * 10, n = 0.001 * 50, autoScale = True)

setRate(at =    0, rate = 30)
setRate(at = 1000, rate = 60)
setRate(at = 2000, rate = 40)
setRate(at = 4000, rate = 80)

endOfSimulation(at = 5000)
