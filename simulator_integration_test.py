import mock
from nose.tools import *
import os

from simulator import loadBalancingAlgorithms, main

def test_main():
    for algorithm in loadBalancingAlgorithms:
        with mock.patch('sys.argv', [os.getcwd() + '/simulator.py', '--algorithm', algorithm]):
            main()

@raises(SystemExit)
def test_invalid_algorithm():
    with mock.patch('sys.argv', [os.getcwd() + '/simulator.py', '--algorithm', 'non-existant']):
        main()
