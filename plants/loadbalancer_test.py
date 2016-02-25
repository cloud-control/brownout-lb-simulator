from mock import Mock

from loadbalancer import LoadBalancer
from base import SimulatorKernel, Request
 
def test():
    sim = SimulatorKernel(outputDirectory = None)

    server1 = Mock()
    server2 = Mock()

    lb = LoadBalancer(sim)
    lb.addBackend(server1)
    lb.addBackend(server2)

    lb.removeBackend(server2)

    assert str(lb)

class MockServer:
    def __init__(self, sim, latency = 0):
        self.sim = sim
        self.numSeenRequests = 0
        self.latency = latency

    def request(self, request):
        if self.numSeenRequests == 0:
            request.withOptional = True
            request.theta = 1
        else:
            request.withOptional = False
            request.theta = 0
        self.numSeenRequests += 1
        self.sim.add(self.latency, request.onCompleted)

def test_remove_while_request_in_progress():
    sim = SimulatorKernel(outputDirectory = None)

    server1 = MockServer(sim, latency = 10)
    server2 = MockServer(sim, latency = 10)

    lb = LoadBalancer(sim)
    lb.addBackend(server1)
    lb.addBackend(server2)

    onShutdownCompleted = Mock()

    def remove_active_server():
        if server1.numSeenRequests:
            lb.removeBackend(server1, onShutdownCompleted)
        else:
            lb.removeBackend(server2, onShutdownCompleted)

    r1 = Request()
    r1.onCompleted = Mock()
    sim.add(0, lambda: lb.request(r1))
    sim.add(1, lambda: remove_active_server())
    sim.add(1, lambda: lb.request(Request()))
    sim.add(2, lambda: lb.request(Request()))
    sim.add(2, lambda: lb.request(Request()))
    sim.run()

    r1.onCompleted.assert_called_once_with()
    onShutdownCompleted.assert_called_once_with()
    assert server1.numSeenRequests == 1 or server2.numSeenRequests == 1
    assert server1.numSeenRequests == 3 or server2.numSeenRequests == 3
