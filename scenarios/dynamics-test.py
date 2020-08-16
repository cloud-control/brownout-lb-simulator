addServer(y = 0.07, n =  0.001)


setRate(at =    0, rate = 300.0)
#setRate(at =    0, rate = 600.0)
for i in range(0,20):
    setRate(at =    200+i*200, rate = 150.0)
    setRate(at =    250.0+i*200, rate = 450.0)
    setRate(at =    300.0+i*200, rate = 300.0)


endOfSimulation(at = 2150)
