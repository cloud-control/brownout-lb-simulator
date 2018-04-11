speedfactor = 1.0
addServer(at=0.0, y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(at=0.0, y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(at=0.0, y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(at=0.0, y = speedfactor * 0.07    , n = speedfactor * 0.001    )
addServer(at=0.0, y = speedfactor * 0.07    , n = speedfactor * 0.001    )


setRate(at =    0, rate = 250.0)

serverSpeeds = []
serverSpeeds.append((0.07, 0.001))
serverSpeeds.append((0.05, 0.001))
serverSpeeds.append((0.02, 0.001))
changeActiveServers(at=50.0, nbrActive=3, serverSpeeds=serverSpeeds)
serverSpeeds.append((0.06, 0.001))
serverSpeeds.append((0.06, 0.001))
serverSpeeds.append((0.06, 0.001))

changeActiveServers(at=100.0, nbrActive=6, serverSpeeds=serverSpeeds)
setRate(at =    150.0, rate = 500.0)


endOfSimulation(at = 200)