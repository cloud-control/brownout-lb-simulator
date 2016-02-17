from Clients import *
from SimulatorKernel import *

class MockServer:
    def __init__(self, sim):
        self.sim = sim
        self.numSeenRequests = 0

    def request(self, request):
        if self.numSeenRequests == 0:
            request.withOptional = True
        else:
            request.withOptional = False
        self.numSeenRequests += 1
        self.sim.add(0, request.onCompleted)

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
