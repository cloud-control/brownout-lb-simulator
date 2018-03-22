speedfactor = 0.70#0.70 previously
#speedfactor1 = 0.70
addServer(y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(y = speedfactor * 0.07    , n = speedfactor * 0.001    )

"""addServer(y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(y = speedfactor * 0.07    , n = speedfactor * 0.001    )"""
"""addServer(y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(y = speedfactor * 0.07    , n = speedfactor * 0.001    )"""

"""changeServiceTime(at = 0.0, serverId = 0, y = speedfactor*2*0.07, n = speedfactor*2*0.001)
changeServiceTime(at = 0.0, serverId = 1, y = speedfactor*2*0.07, n = speedfactor*2*0.001)
changeServiceTime(at = 0.0, serverId = 2, y = speedfactor*2*0.07, n = speedfactor*2*0.001)"""

#addServer(y = speedfactor * 0.07 * 2.0, n = speedfactor * 0.001 * 2.0)
#addServer(y = speedfactor * 0.07 * 4.0, n = speedfactor * 0.001 * 4.0)

#for i in range(1, 21):
#	time = (i-1)*400.0
#	setRate(at =    time, rate = 100.0)
#	setRate(at =    time+300.0, rate = 0.0)

setRate(at =    0, rate = 300.0)
#setRate(at =    0, rate = 600.0)
for i in range(0,10):
    setRate(at =    200+i*200, rate = 150.0)
    setRate(at =    250.0+i*200, rate = 450.0)
    setRate(at =    300.0+i*200, rate = 300.0)


"""changeServiceTime(at=0.0, serverId=0, y=speedfactor / 2.0 * 0.07, n=speedfactor / 2.0* 0.001)
changeServiceTime(at=0.0, serverId=1, y=speedfactor / 2.0 * 0.07, n=speedfactor / 2.0* 0.001)
changeServiceTime(at=0.0, serverId=2, y=speedfactor / 2.0 * 0.07, n=speedfactor / 2.0* 0.001)
changeServiceTime(at=0.0, serverId=3, y=speedfactor / 2.0 * 0.07, n=speedfactor / 2.0 * 0.001)
changeServiceTime(at=0.0, serverId=4, y=speedfactor / 2.0 * 0.07, n=speedfactor / 2.0* 0.001)


for i in range(0,10):
    changeServiceTime(at=200+i*200, serverId=0, y=speedfactor * 1.0 * 0.07, n=speedfactor * 1.0* 0.001)
    changeServiceTime(at=200 + i * 200, serverId=1, y=speedfactor * 1.0 * 0.07, n=speedfactor * 1.0* 0.001)
    changeServiceTime(at=200 + i * 200, serverId=2, y=speedfactor * 1.0 * 0.07, n=speedfactor * 1.0* 0.001)
    changeServiceTime(at=200 + i * 200, serverId=3, y=speedfactor * 1.0 * 0.07, n=speedfactor * 1.0 * 0.001)
    changeServiceTime(at=200 + i * 200, serverId=4, y=speedfactor * 1.0 * 0.07, n=speedfactor * 1.0* 0.001)
    changeServiceTime(at=250+i*200, serverId=0, y=speedfactor / 4.0 * 0.07, n=speedfactor / 4.0 * 0.001)
    changeServiceTime(at=250 + i * 200, serverId=1, y=speedfactor / 4.0 * 0.07, n=speedfactor / 4.0 * 0.001)
    changeServiceTime(at=250 + i * 200, serverId=2, y=speedfactor / 4.0 * 0.07, n=speedfactor / 4.0 * 0.001)
    changeServiceTime(at=250 + i * 200, serverId=3, y=speedfactor / 4.0 * 0.07, n=speedfactor / 4.0 * 0.001)
    changeServiceTime(at=250 + i * 200, serverId=4, y=speedfactor / 4.0 * 0.07, n=speedfactor / 4.0  * 0.001)
    changeServiceTime(at=300+i*200, serverId=0, y=speedfactor / 2.0 * 0.07, n=speedfactor / 2.0 * 0.001)
    changeServiceTime(at=300 + i * 200, serverId=1, y=speedfactor / 2.0 * 0.07, n=speedfactor / 2.0 * 0.001)
    changeServiceTime(at=300 + i * 200, serverId=2, y=speedfactor / 2.0 * 0.07, n=speedfactor / 2.0 * 0.001)
    changeServiceTime(at=300 + i * 200, serverId=3, y=speedfactor / 2.0 * 0.07, n=speedfactor / 2.0 * 0.001)
    changeServiceTime(at=300 + i * 200, serverId=4, y=speedfactor / 2.0 * 0.07, n=speedfactor / 2.0 * 0.001)"""

endOfSimulation(at = 2150)
