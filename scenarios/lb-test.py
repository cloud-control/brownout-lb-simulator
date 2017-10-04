speedfactor = 0.70
addServer(y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(y = speedfactor * 0.07 * 2.0, n = speedfactor * 0.001 * 2.0)
addServer(y = speedfactor * 0.07 * 4.0, n = speedfactor * 0.001 * 4.0)

for i in range(1, 21):
	time = (i-1)*400.0
	setRate(at =    time, rate = 100.0)
	setRate(at =    time+300.0, rate = 0.0)
	
#setRate(at =    0, rate = 100.0)
#setRate(at =    300.0, rate = 0.0)

endOfSimulation(at = 8000)
