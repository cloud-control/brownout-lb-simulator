# Scenario to test the cascaded replica controller

# Add one server
addServer(y = 0.07, n = 0.001)


"""addClients(at =    0, n = 50 )
addClients(at =    200, n = 100 )
delClients(at =    400, n = 100 )
addClients(at =    600, n = 100 )
delClients(at =    800, n = 100 )"""

#setRate(at =    0, rate = 100.0)

for i in range(1, 21):

	time = (i-1)*300.0
	setRate(at =    time, rate = 20.0)
	setRate(at =    time + 60.0, rate = 100.0)
	setRate(at =    time + 120.0, rate = 30.0)
	setRate(at =    time + 180.0, rate = 70.0)
	setRate(at =    time + 240.0, rate = 20.0)
	




"""setRate(at =    1000, rate = 100.0)
setRate(at =    1200, rate = 25.0)
setRate(at =    1400, rate = 100.0)
setRate(at =    1600, rate = 25.0)
setRate(at =    1800, rate = 100.0)"""
"""setRate(at =    2000, rate = 25.0)
setRate(at =    2200, rate = 100.0)
setRate(at =    2400, rate = 25.0)
setRate(at =    2600, rate = 100.0)
setRate(at =    2800, rate = 25.0)
setRate(at =    3000, rate = 100.0)
setRate(at =    3200, rate = 25.0)
setRate(at =    3400, rate = 100.0)
setRate(at =    3600, rate = 25.0)
setRate(at =    3800, rate = 100.0)"""

"""
for i in range(0, 20):
	time = i*200.0
	arrivals = 25 + i
	setRate(at =    time, rate = arrivals)"""
	

endOfSimulation(at = 6000)
