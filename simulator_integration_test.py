import mock
import os

from simulator import loadBalancingAlgorithms, main

def test_main():
    for algorithm in loadBalancingAlgorithms:
        with mock.patch('sys.argv', [os.getcwd() + '/simulator.py', '--algorithm', algorithm]):
            main()
