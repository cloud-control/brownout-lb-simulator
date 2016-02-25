from base import SimulatorKernel
from clients import ClosedLoopClient, OpenLoopClient

eps = 10e-6

class MockServer:
    def __init__(self, sim, latency = 0):
        self.sim = sim
        self.numSeenRequests = 0
        self.latency = latency

    def request(self, request):
        if self.numSeenRequests == 0:
            request.withOptional = True
        else:
            request.withOptional = False
        self.numSeenRequests += 1
        self.sim.add(self.latency, request.onCompleted)

def test_open_client():
    sim = SimulatorKernel()
    server = MockServer(sim)
    clients = OpenLoopClient(sim, server)
    clients.setRate(10)
    sim.run(until = 100)

    # TODO: Better statistical test
    assert server.numSeenRequests >  900, server.numSeenRequests
    assert server.numSeenRequests < 1100, server.numSeenRequests

    assert clients.numCompletedRequests == server.numSeenRequests
    assert clients.numCompletedRequestsWithOptional == 1
    assert len(clients.responseTimes) == clients.numCompletedRequests
    assert max(clients.responseTimes) == 0

def test_open_client_with_latency():
    sim = SimulatorKernel()
    server = MockServer(sim, latency = 1)
    clients = OpenLoopClient(sim, server)
    clients.setRate(10)
    sim.run(until = 100)

    # TODO: Better statistical test
    assert server.numSeenRequests >  900, server.numSeenRequests
    assert server.numSeenRequests < 1100, server.numSeenRequests

    assert server.numSeenRequests - clients.numCompletedRequests <= 20, server.numSeenRequests - clients.numCompletedRequests
    assert clients.numCompletedRequestsWithOptional == 1
    assert len(clients.responseTimes) == clients.numCompletedRequests
    assert abs(max(clients.responseTimes) - 1) < eps

def test_open_client_off():
    sim = SimulatorKernel()
    server = MockServer(sim)
    clients = OpenLoopClient(sim, server)
    clients.setRate(10)
    sim.add(10, lambda: clients.setRate(0))
    sim.run(until = 100)

    assert server.numSeenRequests < 110, server.numSeenRequests

def test_open_client_str():
    sim = SimulatorKernel()
    server = MockServer(sim)
    clients = OpenLoopClient(sim, server)
    assert str(clients)

def test_closed_client():
    sim = SimulatorKernel()
    server = MockServer(sim)
    client = ClosedLoopClient(sim, server)
    sim.run(until = 100)

    # TODO: Better statistical test
    assert server.numSeenRequests >  70, server.numSeenRequests
    assert server.numSeenRequests < 130, server.numSeenRequests

    assert client.numCompletedRequests == server.numSeenRequests
    assert client.numCompletedRequestsWithOptional == 1
    assert len(client.responseTimes) == client.numCompletedRequests
    assert max(client.responseTimes) == 0

def test_closed_client_with_latency():
    sim = SimulatorKernel()
    server = MockServer(sim, latency = 1)
    client = ClosedLoopClient(sim, server)
    sim.run(until = 100)

    # TODO: Better statistical test
    assert server.numSeenRequests > 40, server.numSeenRequests
    assert server.numSeenRequests < 60, server.numSeenRequests

    assert server.numSeenRequests - client.numCompletedRequests <= 1
    assert client.numCompletedRequestsWithOptional == 1
    assert len(client.responseTimes) == client.numCompletedRequests
    assert abs(max(client.responseTimes) - 1.0) < eps, max(client.responseTimes)

def test_closed_client_off():
    sim = SimulatorKernel()
    server = MockServer(sim)
    client = ClosedLoopClient(sim, server)
    sim.add(10, lambda: client.deactivate())
    sim.run(until = 100)

    assert server.numSeenRequests < 20, server.numSeenRequests

def test_closed_client_str():
    sim = SimulatorKernel()
    server = MockServer(sim)
    client = ClosedLoopClient(sim, server)
    assert str(client)
