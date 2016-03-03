import mock
from nose.tools import *

from simulator import loadBalancingAlgorithms, main

RESIDUE_TABLE={
    'weighted-RR'          : ('final-results', 'weighted-RR         , mm_queueifac        ,   39428,    8704, 0.221, 1.146, 2.040, 3.089, 6.350, 0.417'),
    'theta-diff'           : ('final-results', 'theta-diff          , mm_queueifac        ,   39428,    8704, 0.221, 1.146, 2.040, 3.089, 6.350, 0.417'),
    'SQF'                  : ('final-results', 'SQF                 , mm_queueifac        ,   39428,    8704, 0.221, 1.146, 2.040, 3.089, 6.350, 0.417'),
    'SQF-plus'             : ('final-results', 'SQF-plus            , mm_queueifac        ,   39428,    8704, 0.221, 1.146, 2.040, 3.089, 6.350, 0.417'),
    'FRF'                  : ('final-results', 'FRF                 , mm_queueifac        ,   39428,    8704, 0.221, 1.146, 2.040, 3.089, 6.350, 0.417'),
    'equal-thetas'         : ('final-results', 'equal-thetas        , mm_queueifac        ,   39428,    8704, 0.221, 1.146, 2.040, 3.089, 6.350, 0.417'),
    'equal-thetas-SQF'     : ('final-results', 'equal-thetas-SQF    , mm_queueifac        ,   39428,    8704, 0.221, 1.146, 2.040, 3.089, 6.350, 0.417'),
    'FRF-EWMA'             : ('final-results', 'FRF-EWMA            , mm_queueifac        ,   39428,    8704, 0.221, 1.146, 2.040, 3.089, 6.350, 0.417'),
    'predictive'           : ('final-results', 'predictive          , mm_queueifac        ,   39428,    8704, 0.221, 1.146, 2.040, 3.089, 6.350, 0.417'),
    '2RC'                  : ('final-results', '2RC                 , mm_queueifac        ,   39428,    8704, 0.221, 1.146, 2.040, 3.089, 6.350, 0.417'),
    'RR'                   : ('final-results', 'RR                  , mm_queueifac        ,   39428,    8704, 0.221, 1.146, 2.040, 3.089, 6.350, 0.417'),
    'random'               : ('final-results', 'random              , mm_queueifac        ,   39428,    8704, 0.221, 1.146, 2.040, 3.089, 6.350, 0.417'),
    'theta-diff-plus'      : ('final-results', 'theta-diff-plus     , mm_queueifac        ,   39428,    8704, 0.221, 1.146, 2.040, 3.089, 6.350, 0.417'),
    'ctl-simplify'         : ('final-results', 'ctl-simplify        , mm_queueifac        ,   39428,    8704, 0.221, 1.146, 2.040, 3.089, 6.350, 0.417'),
    'equal-thetas-fast'    : ('final-results', 'equal-thetas-fast   , mm_queueifac        ,   39428,    8704, 0.221, 1.146, 2.040, 3.089, 6.350, 0.417'),
    'theta-diff-plus-SQF'  : ('final-results', 'theta-diff-plus-SQF , mm_queueifac        ,   39428,    8704, 0.221, 1.146, 2.040, 3.089, 6.350, 0.417'),
    'theta-diff-plus-fast' : ('final-results', 'theta-diff-plus-fast, mm_queueifac        ,   39428,    8704, 0.221, 1.146, 2.040, 3.089, 6.350, 0.417'),
    'SRTF'                 : ('final-results', 'SRTF                , mm_queueifac        ,   39428,    8704, 0.221, 1.146, 2.040, 3.089, 6.350, 0.417'),
    'equal-thetas-fast-mul': ('final-results', 'equal-thetas-fast-mul, mm_queueifac        ,   39428,    8704, 0.221, 1.146, 2.040, 3.089, 6.350, 0.417'),
}

@mock.patch('base.SimulatorKernel.output')
def check_residue(algorithm, output):
    """
    Ensure the algorithm behaves exactly the same as it used to, in preparation for some intrusive refactoring.
    """
    with mock.patch('sys.argv', [
            './simulator.py',
            '--rc', 'mm_queueifac',
            '--algorithm', algorithm,
        ]):
        main()

    print output.mock_calls[-1]
    output.assert_called_with(*RESIDUE_TABLE[algorithm])

def test_residue():
    for algorithm in loadBalancingAlgorithms:
            yield check_residue, algorithm
