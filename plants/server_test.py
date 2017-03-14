from mock import Mock

from server import Server
from base import Request, SimulatorKernel

eps = 10e-6

def test_without_controller():
    completedRequests = []

    sim = SimulatorKernel(outputDirectory = None)

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

def test_with_controller_always_no():
    completedRequests = []

    controller = Mock()
    controller.withOptional.return_value = False, 0

    sim = SimulatorKernel(outputDirectory = None)
    server = Server(sim,
            serviceTimeY = 10, serviceTimeYVariance = 0,
            serviceTimeN =  1, serviceTimeNVariance = 0)
    server.controller = controller

    r = Request()
    r.onCompleted = lambda: completedRequests.append(r)
    sim.add(0, lambda: server.request(r))
    
    r2 = Request()
    r2.onCompleted = lambda: completedRequests.append(r2)
    sim.add(0, lambda: server.request(r2))

    sim.run()

    controller.withOptional.assert_called_with()

    assert set(completedRequests) == set([ r, r2 ])
    assert server.getActiveTime() == 2.0, server.getActiveTime()

def test_with_controller_always_yes():
    completedRequests = []

    controller = Mock()
    controller.withOptional.return_value = True, 1

    sim = SimulatorKernel(outputDirectory = None)
    server = Server(sim,
            serviceTimeY = 10, serviceTimeYVariance = 0,
            serviceTimeN =  1, serviceTimeNVariance = 0)
    server.controller = controller

    r = Request()
    r.onCompleted = lambda: completedRequests.append(r)
    sim.add(0, lambda: server.request(r))
    
    r2 = Request()
    r2.onCompleted = lambda: completedRequests.append(r2)
    sim.add(0, lambda: server.request(r2))

    sim.run()

    controller.withOptional.assert_called_with()

    assert set(completedRequests) == set([ r, r2 ])
    assert abs(server.getActiveTime() - 20.0) < eps, server.getActiveTime()

def test_without_controller_fifo():
    completedRequests = []
    endTimes = []
    sim = SimulatorKernel(outputDirectory = None)

    server = Server(sim, serviceTimeY = 1, serviceTimeYVariance = 0,
                    timeSlice = 100)

    def onCompleted(r):
        completedRequests.append(r)
        endTimes.append(sim.now)

    r = Request()
    r.onCompleted = lambda: onCompleted(r)
    sim.add(0, lambda: server.request(r))
    
    r2 = Request()
    r2.onCompleted = lambda: onCompleted(r2)
    sim.add(0, lambda: server.request(r2))

    sim.run()

    assert set(completedRequests) == set([ r, r2 ])
    assert endTimes == [1, 2], endTimes
    assert server.getActiveTime() == 2.0, server.getActiveTime()

def test_without_controller_fifo_multiple_cores():
    completedRequests = []
    endTimes = []
    sim = SimulatorKernel(outputDirectory = None)

    server = Server(sim, serviceTimeY = 1, serviceTimeYVariance = 0,
                    timeSlice = 100, numCores = 2)

    def onCompleted(r):
        completedRequests.append(r)
        endTimes.append(sim.now)

    r = Request()
    r.onCompleted = lambda: onCompleted(r)
    sim.add(0, lambda: server.request(r))
    
    r2 = Request()
    r2.onCompleted = lambda: onCompleted(r2)
    sim.add(0, lambda: server.request(r2))

    r3 = Request()
    r3.onCompleted = lambda: onCompleted(r3)
    sim.add(0, lambda: server.request(r3))

    sim.run()

    assert endTimes == [1, 1, 2], endTimes
    assert server.getActiveTime() == 3.0, server.getActiveTime()
