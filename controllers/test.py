from __future__ import print_function

import argparse
import os
import sys

from mock import Mock

from base import SimulatorKernel
from controllers import loadControllerFactories

def test_replica_controller_factories():
    for replicaControllerFactory in loadControllerFactories('server'):
        assert replicaControllerFactory.getName()
        check_replica_controller_factory(replicaControllerFactory)

def check_replica_controller_factory(replicaControllerFactory):
    parser = argparse.ArgumentParser()
    # TODO: avoid code duplication
    parser.add_argument('--rcSetpoint', default = 1.0)
    parser.add_argument('--rcPercentile', default = 95)
    replicaControllerFactory.addCommandLine(parser)
	
    args = parser.parse_args(args = [])
    replicaControllerFactory.parseCommandLine(args)

    sim = SimulatorKernel(outputDirectory = None)
    controller = replicaControllerFactory.newInstance(sim, "blah")

    # smoke test
    controller.reportData(1, 10, 2, 2)

    sim.run()

    assert str(controller) == "blah"
    assert controller.withOptional()[0] in [ False, True ]
    assert 0 <= controller.withOptional()[1] <= 1
