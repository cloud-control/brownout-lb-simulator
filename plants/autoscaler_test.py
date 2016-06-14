import mock
import random
from nose.tools import *

from .autoscaler import AutoScaler, BackendStatus
from base import SimulatorKernel, Request

eps=10e-6

def assert_autoscaler_status_is(autoScaler, stopped, starting, started, stopping):
    status = autoScaler.getStatus()

    expected = (stopped, starting, started, stopping)
    actual = (status[BackendStatus.STOPPED], status[BackendStatus.STARTING],
            status[BackendStatus.STARTED], status[BackendStatus.STOPPING])
    assert expected == actual, \
        "AutoScaler status is incorrect: expected {0}, actual {1}".\
            format(expected, actual)

class MockLoadBalancer:
    def __init__(self, sim, latency = 0):
        self.sim = sim
        self.numSeenRequests = 0
        self.latency = latency
        self.lastRemovedBackend = None
        self.addBackend = mock.Mock()

    def request(self, request):
        if self.numSeenRequests == 0:
            request.withOptional = True
        else:
            request.withOptional = False
        self.numSeenRequests += 1
        self.sim.add(self.latency, request.onCompleted)

    def removeBackend(self, backend, onShutdown):
        self.sim.add(self.latency, onShutdown)
        self.lastRemovedBackend = backend

def test_request_hooks():
    sim = SimulatorKernel(outputDirectory = None)

    loadBalancer = MockLoadBalancer(sim, latency = 1)
    autoScalerController = mock.Mock()
    autoScalerController.controlInterval = 1
    autoScalerController.onRequest = mock.Mock(return_value=None)
    autoScalerController.onCompleted = mock.Mock(return_value=None)
    autoScalerController.onControlPeriod = mock.Mock(return_value=None)
    autoScalerController.onStatus = mock.Mock(return_value=None)

    autoScaler = AutoScaler(sim, loadBalancer, controller = autoScalerController)
    assert str(autoScaler)

    server1 = mock.Mock(name = 'server1')
    server2 = mock.Mock(name = 'server2')
    autoScaler.addBackend(server1)
    autoScaler.addBackend(server2)

    r = Request()
    autoScaler.request(r)
    sim.add(100, lambda: autoScaler.scaleUp())
    sim.run(until = 1000)

    # TODO: Check exact call parameters
    assert autoScalerController.onRequest.call_count == 1, autoScalerController.onRequest.call_count
    assert autoScalerController.onCompleted.call_count == 1, autoScalerController.onCompleted.call_count
    assert autoScalerController.onStatus.call_count == 3, autoScalerController.onStatus.call_count
    assert autoScalerController.onControlPeriod.call_count == 1000, autoScalerController.onControlPeriod.call_count

@raises(RuntimeError)
def test_scale_up_error():
    sim = SimulatorKernel(outputDirectory = None)

    loadBalancer = MockLoadBalancer(sim, latency = 1)
    autoScaler = AutoScaler(sim, loadBalancer, startupDelay = 60)
    assert str(autoScaler)

    server1 = mock.Mock(name = 'server1')
    autoScaler.addBackend(server1)
    autoScaler.scaleUp()
    autoScaler.scaleUp()

@raises(RuntimeError)
def test_scale_down_error():
    sim = SimulatorKernel(outputDirectory = None)

    loadBalancer = MockLoadBalancer(sim, latency = 1)
    autoScaler = AutoScaler(sim, loadBalancer, startupDelay = 60)
    assert str(autoScaler)

    server1 = mock.Mock(name = 'server1')
    autoScaler.addBackend(server1)
    autoScaler.scaleUp()
    autoScaler.scaleDown()
    autoScaler.scaleDown()

def test_scale_up_and_down():
    sim = SimulatorKernel(outputDirectory = None)

    loadBalancer = MockLoadBalancer(sim, latency = 1)
    autoScaler = AutoScaler(sim, loadBalancer, startupDelay = 60)
    assert str(autoScaler)

    server1 = mock.Mock(name = 'server1')
    server2 = mock.Mock(name = 'server2')
    autoScaler.addBackend(server1)
    autoScaler.addBackend(server2)

    sim.add(0, lambda: assert_autoscaler_status_is(autoScaler, 2, 0, 0, 0))

    sim.add(10, lambda: autoScaler.scaleUp())
    sim.add(10, lambda: assert_autoscaler_status_is(autoScaler, 1, 1, 0, 0))

    sim.add(10+59, lambda: loadBalancer.addBackend.assert_not_called()) # startup delay
    sim.add(10+59, lambda: assert_autoscaler_status_is(autoScaler, 1, 1, 0, 0))

    sim.add(10+60+eps, lambda: assert_autoscaler_status_is(autoScaler, 1, 0, 1, 0))
    sim.add(10+60+eps, lambda: loadBalancer.addBackend.assert_called_with(server1))

    sim.add(100, lambda: autoScaler.scaleUp())
    sim.add(100, lambda: assert_autoscaler_status_is(autoScaler, 0, 1, 1, 0))

    sim.add(100+59, lambda: assert_autoscaler_status_is(autoScaler, 0, 1, 1, 0))

    sim.add(100+60+eps, lambda: assert_autoscaler_status_is(autoScaler, 0, 0, 2, 0))
    sim.add(100+60+eps, lambda: loadBalancer.addBackend.assert_called_with(server2))

    sim.add(200, lambda: autoScaler.scaleDown())
    sim.add(200, lambda: assert_autoscaler_status_is(autoScaler, 0, 0, 1, 1))

    sim.add(200+1-eps, lambda: assert_autoscaler_status_is(autoScaler, 0, 0, 1, 1))
    sim.add(200+1+eps, lambda: assert_autoscaler_status_is(autoScaler, 1, 0, 1, 0))

    sim.run()

    assert loadBalancer.lastRemovedBackend == server2

def test_scale_up_and_down_multiple():
    sim = SimulatorKernel(outputDirectory = None)

    loadBalancer = MockLoadBalancer(sim, latency = 1)
    autoScaler = AutoScaler(sim, loadBalancer, startupDelay = 60)
    assert str(autoScaler)

    server1 = mock.Mock(name = 'server1')
    server2 = mock.Mock(name = 'server2')
    server3 = mock.Mock(name = 'server3')
    server4 = mock.Mock(name = 'server4')
    autoScaler.addBackend(server1)
    autoScaler.addBackend(server2)
    autoScaler.addBackend(server3)
    autoScaler.addBackend(server4)

    sim.add(0, lambda: assert_autoscaler_status_is(autoScaler, 4, 0, 0, 0))

    sim.add(10, lambda: autoScaler.scaleTo(2))
    sim.add(10, lambda: assert_autoscaler_status_is(autoScaler, 2, 2, 0, 0))

    sim.add(10+59, lambda: loadBalancer.addBackend.assert_not_called()) # startup delay
    sim.add(10+59, lambda: assert_autoscaler_status_is(autoScaler, 2, 2, 0, 0))

    sim.add(10+60+eps, lambda: assert_autoscaler_status_is(autoScaler, 2, 0, 2, 0))
    calls1 = [mock.call(server1), mock.call(server2)]
    sim.add(10+60+eps, lambda: loadBalancer.addBackend.assert_has_calls(calls1))

    sim.add(100, lambda: autoScaler.scaleTo(4))
    sim.add(100, lambda: assert_autoscaler_status_is(autoScaler, 0, 2, 2, 0))

    sim.add(100+59, lambda: assert_autoscaler_status_is(autoScaler, 0, 2, 2, 0))

    sim.add(100+60+eps, lambda: assert_autoscaler_status_is(autoScaler, 0, 0, 4, 0))
    calls2 = [mock.call(server3), mock.call(server4)]
    sim.add(100+60+eps, lambda: loadBalancer.addBackend.assert_has_calls(calls2))

    sim.add(200, lambda: autoScaler.scaleTo(1))
    sim.add(200, lambda: assert_autoscaler_status_is(autoScaler, 0, 0, 1, 3))

    sim.add(200+1-eps, lambda: assert_autoscaler_status_is(autoScaler, 0, 0, 1, 3))
    sim.add(200+1+eps, lambda: assert_autoscaler_status_is(autoScaler, 3, 0, 1, 0))

    sim.run()

    assert loadBalancer.lastRemovedBackend == server2

@raises(RuntimeError)
def test_invalid_action():
    sim = SimulatorKernel(outputDirectory = None)

    loadBalancer = MockLoadBalancer(sim, latency = 1)
    autoScalerController = mock.Mock()
    autoScalerController.controlInterval = 1
    autoScalerController.onRequest = mock.Mock(return_value=-2)
    autoScalerController.onCompleted = mock.Mock(return_value=None)
    autoScalerController.onControlPeriod = mock.Mock(return_value=None)
    autoScalerController.onStatus = mock.Mock(return_value=None)

    autoScaler = AutoScaler(sim, loadBalancer, controller = autoScalerController)
    assert str(autoScaler)

    server1 = mock.Mock(name = 'server1')
    server2 = mock.Mock(name = 'server2')
    autoScaler.addBackend(server1)
    autoScaler.addBackend(server2)

    r = Request()
    autoScaler.request(r)
    sim.add(100, lambda: autoScaler.scaleUp())
    sim.run()

def test_random_startup_delay(average=60, variance=10, values_to_test=10):
    rng = random.Random()
    startupDelayFunc = lambda: rng.normalvariate(average, variance)

    # "predict" future random delays by resetting the PRNG's seed
    random_delays = []
    rng.seed(1)
    for _ in range(values_to_test):
        random_delays.append(startupDelayFunc())
    rng.seed(1)

    sim = SimulatorKernel(outputDirectory = None)

    loadBalancer = MockLoadBalancer(sim, latency = 1)
    autoScaler = AutoScaler(sim, loadBalancer, startupDelay = startupDelayFunc)
    assert str(autoScaler)

    for i in range(values_to_test):
        server = mock.Mock(name = 'server' + str(i))
        autoScaler.addBackend(server)

    # NOTE: `lambda i=i` is required to capture the current value of `i` inside
    # the lambda.
    currentTime = 0
    for i in range(values_to_test):
        currentTime += 1
        sim.add(currentTime, lambda i=i: autoScaler.scaleTo(i+1))
        currentTime += random_delays[i]
        sim.add(currentTime-eps, lambda i=i:
                assert_autoscaler_status_is(autoScaler, values_to_test-i-1, 1, i, 0))
        sim.add(currentTime+eps, lambda i=i:
                assert_autoscaler_status_is(autoScaler, values_to_test-i-1, 0, i+1, 0))
    
    sim.run()

    assert_autoscaler_status_is(autoScaler, 0, 0, values_to_test, 0)
