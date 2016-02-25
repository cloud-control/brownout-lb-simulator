from mock import Mock

from loadbalancer import LoadBalancer
from base import SimulatorKernel
 
def test():
    sim = SimulatorKernel(outputDirectory = None)

    server1 = Mock()
    server2 = Mock()

    lb = LoadBalancer(sim)
    lb.addBackend(server1)
    lb.addBackend(server2)

    lb.removeBackend(server2)

    assert str(lb)

    # TODO: Test for removal delay
