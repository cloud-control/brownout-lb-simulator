from mock import Mock
from nose.tools import nottest

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

@nottest
def test_without_controller_processor_sharing():
    """
    We do not seem to implement processor sharing quite correctly.
    This test serves to prove it. Enable it after the server is fixed.
    """
    completedRequests = []

    sim = SimulatorKernel(outputDirectory = None)

    server = Server(sim, timeSlice = 100)

    r = Request()
    r.remainingTime = 250
    r.onCompleted = lambda: completedRequests.append(r)
    sim.add(0, lambda: server.request(r))
    
    r2 = Request()
    r2.remainingTime = 100
    r2.onCompleted = lambda: completedRequests.append(r2)
    sim.add(50, lambda: server.request(r2))

    sim.run()

    assert r.completion  == 350, r.completion
    assert r2.completion == 200, r2.completion

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
