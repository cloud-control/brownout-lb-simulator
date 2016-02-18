from Request import *
from Server import *
from SimulatorKernel import *

def test():
    completedRequests = []

    sim = SimulatorKernel()
    server = Server(sim, serviceTimeY = 1, serviceTimeYVariance = 0)

    r = Request()
    r.onCompleted = lambda: completedRequests.append(r)
    sim.add(0, lambda: server.request(r))
    
    r2 = Request()
    r2.onCompleted = lambda: completedRequests.append(r2)
    sim.add(0, lambda: server.request(r2))

    sim.run()

    assert set(completedRequests) == set([ r, r2 ])
    assert server.getActiveTime() == 2.0, server.getActiveTime()
