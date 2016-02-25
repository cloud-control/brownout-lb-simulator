import mock
from nose.tools import *

from AutoScaler import AutoScaler, BackendStatus
from SimulatorKernel import SimulatorKernel
from Request import Request

eps=10e-6

class MockLoadBalancer:
    def __init__(self, sim, latency = 0):
        self.sim = sim
        self.numSeenRequests = 0
        self.latency = latency
        self.lastRemovedBackend = None

    def request(self, request):
        if self.numSeenRequests == 0:
            request.withOptional = True
        else:
            request.withOptional = False
        self.numSeenRequests += 1
        self.sim.add(self.latency, request.onCompleted)

    addBackend = mock.Mock()

    def removeBackend(self, backend, onShutdown):
        self.sim.add(self.latency, onShutdown)
        self.lastRemovedBackend = backend

def test_request_hooks():
    sim = SimulatorKernel(outputDirectory = None)

    loadBalancer = MockLoadBalancer(sim, latency = 1)
    autoScalerController = mock.Mock()
    autoScaler = AutoScaler(sim, loadBalancer, controller = autoScalerController)
    assert str(autoScaler)

    server1 = mock.Mock(name = 'server1')
    server2 = mock.Mock(name = 'server2')
    autoScaler.addBackend(server1)
    autoScaler.addBackend(server2)

    r = Request()
    autoScaler.request(r)
    sim.run()
    assert autoScalerController.onRequest.call_count == 1, autoScalerController.onRequest.call_count
    assert autoScalerController.onCompleted.call_count == 1, autoScalerController.onCompleted.call_count

@raises(RuntimeError)
def test_scale_up_error():
    sim = SimulatorKernel(outputDirectory = None)

    loadBalancer = MockLoadBalancer(sim, latency = 1)
    autoScalerController = mock.Mock()
    autoScaler = AutoScaler(sim, loadBalancer, controller = autoScalerController, startupDelay = 60)
    assert str(autoScaler)

    server1 = mock.Mock(name = 'server1')
    autoScaler.addBackend(server1)
    autoScaler.scaleUp()
    autoScaler.scaleUp()

@raises(RuntimeError)
def test_scale_down_error():
    sim = SimulatorKernel(outputDirectory = None)

    loadBalancer = MockLoadBalancer(sim, latency = 1)
    autoScalerController = mock.Mock()
    autoScaler = AutoScaler(sim, loadBalancer, controller = autoScalerController, startupDelay = 60)
    assert str(autoScaler)

    server1 = mock.Mock(name = 'server1')
    autoScaler.addBackend(server1)
    autoScaler.scaleUp()
    autoScaler.scaleDown()
    autoScaler.scaleDown()

def test_scale_up_and_down():
    sim = SimulatorKernel(outputDirectory = None)

    loadBalancer = MockLoadBalancer(sim, latency = 1)
    autoScalerController = mock.Mock()
    autoScaler = AutoScaler(sim, loadBalancer, controller = autoScalerController, startupDelay = 60)
    assert str(autoScaler)

    server1 = mock.Mock(name = 'server1')
    server2 = mock.Mock(name = 'server2')
    autoScaler.addBackend(server1)
    autoScaler.addBackend(server2)

    def assert_autoscaler_status_is(stopped, starting, started, stopping):
        status = autoScaler.getStatus()
        assert status[BackendStatus.STOPPED ] == stopped , stopped
        assert status[BackendStatus.STARTING] == starting, starting
        assert status[BackendStatus.STARTED ] == started , started
        assert status[BackendStatus.STOPPING] == stopping, stopping

    sim.add(0, lambda: assert_autoscaler_status_is(2, 0, 0, 0))

    sim.add(10, lambda: autoScaler.scaleUp())
    sim.add(10, lambda: assert_autoscaler_status_is(1, 1, 0, 0))

    sim.add(10+59, lambda: loadBalancer.addBackend.assert_not_called()) # startup delay
    sim.add(10+59, lambda: assert_autoscaler_status_is(1, 1, 0, 0))

    sim.add(10+60+eps, lambda: assert_autoscaler_status_is(1, 0, 1, 0))
    sim.add(10+60+eps, lambda: loadBalancer.addBackend.assert_called_with(server1))

    sim.add(100, lambda: autoScaler.scaleUp())
    sim.add(100, lambda: assert_autoscaler_status_is(0, 1, 1, 0))

    sim.add(100+59, lambda: assert_autoscaler_status_is(0, 1, 1, 0))

    sim.add(100+60+eps, lambda: assert_autoscaler_status_is(0, 0, 2, 0))
    sim.add(100+60+eps, lambda: loadBalancer.addBackend.assert_called_with(server2))

    sim.add(200, lambda: autoScaler.scaleDown())
    sim.add(200, lambda: assert_autoscaler_status_is(0, 0, 1, 1))

    sim.add(200+1-eps, lambda: assert_autoscaler_status_is(0, 0, 1, 1))
    sim.add(200+1+eps, lambda: assert_autoscaler_status_is(1, 0, 1, 0))

    sim.run()

    assert loadBalancer.lastRemovedBackend == server2
