from __future__ import print_function

import argparse
import os
import sys

from mock import Mock

from SimulatorKernel import *

def test_replica_controller_factories():
    # Load all replica controller factories
    for filename in os.listdir('.'):
        # Not a replica controller factory
        if filename[:4] != "rcf_": continue
        if filename[-3:] != ".py": continue

        print("Loading and testing", filename)

        # Load Python module
        replicaControllerFactory = __import__(os.path.splitext(filename)[0])

        parser = argparse.ArgumentParser()
        # TODO: avoid code duplication
        parser.add_argument('--rcSetpoint', default = 1.0)
        parser.add_argument('--rcPercentile', default = 95)
        replicaControllerFactory.addCommandLine(parser)

        args = parser.parse_args(args = [])
        replicaControllerFactory.parseCommandLine(args)

        sim = SimulatorKernel()
        controller = replicaControllerFactory.newInstance(sim, "blah")

        # smoke test
        controller.reportData(1, 10, 2, 2)

        sim.run()

        assert str(controller) == "blah"
        assert controller.withOptional()[0] in [ False, True ]
        assert 0 <= controller.withOptional()[1] <= 1
