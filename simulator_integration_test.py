import mock
from nose.tools import *

from simulator import loadBalancingAlgorithms, main

@mock.patch('base.SimulatorKernel.output')
def test_main(_):
    for algorithm in loadBalancingAlgorithms:
        with mock.patch('sys.argv', [
                './simulator.py',
                '--algorithm', algorithm,
                ]):
            main()

@mock.patch('base.SimulatorKernel.output')
@raises(SystemExit)
def test_invalid_algorithm(_):
    with mock.patch('sys.argv', [
            './simulator.py',
            '--algorithm',
            'non-existant',
            ]):
        main()

@mock.patch('base.SimulatorKernel.output')
def test_autoscaler(_):
    with mock.patch('sys.argv', [
            './simulator.py',
            '--algorithm', 'SQF',
            '--rc', 'mm_queueifac',
            '--scenario', './scenarios/autoscaling-support.py',
            ]):
        main()
