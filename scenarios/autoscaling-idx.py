# Scenario to test autoscaling

# TODO: Consider adding heterogenity to servers to highlight the strenghts of
# brownout-aware load-balancing algorithms.
addServer(y = 0.07, n = 0.001, autoScale = False) # ensure at least one server is connected
addServer(y = 0.07, n = 0.001, autoScale = True )

setRate(at =    0, rate = 40)

endOfSimulation(at = 2000)
