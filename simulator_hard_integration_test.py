import mock
from nose.tools import *

from simulator import main
from plants import LoadBalancer

_multiprocess_can_split_ = True

RESIDUE_TABLE={
    'weighted-RR'          : ('final-results', 'trivial             , weighted-RR         , mm_queueifac        ,  180425,   95819, 0.531, 0.380, 1.462, 3.916, 10.857, 0.733'),
    'theta-diff'           : ('final-results', 'trivial             , theta-diff          , mm_queueifac        ,  135835,   67482, 0.497, 0.839, 2.278, 21.590, 32.519, 3.197'),
    'SQF'                  : ('final-results', 'trivial             , SQF                 , mm_queueifac        ,  204224,   96625, 0.473, 0.212, 1.032, 2.377, 4.654, 0.439'),
    'SQF-plus'             : ('final-results', 'trivial             , SQF-plus            , mm_queueifac        ,  203380,   99208, 0.488, 0.219, 1.080, 2.346, 4.472, 0.441'),
    'FRF'                  : ('final-results', 'trivial             , FRF                 , mm_queueifac        ,   68860,   51907, 0.754, 2.614, 9.178, 27.523, 31.457, 5.054'),
    'equal-thetas'         : ('final-results', 'trivial             , equal-thetas        , mm_queueifac        ,  175732,   91630, 0.521, 0.418, 1.620, 4.377, 18.047, 0.946'),
    'equal-thetas-SQF'     : ('final-results', 'trivial             , equal-thetas-SQF    , mm_queueifac        ,  204774,   98545, 0.481, 0.209, 0.837, 1.896, 4.462, 0.365'),
    'FRF-EWMA'             : ('final-results', 'trivial             , FRF-EWMA            , mm_queueifac        ,   80191,   34996, 0.436, 2.090, 8.723, 32.686, 34.348, 5.469'),
    'predictive'           : ('final-results', 'trivial             , predictive          , mm_queueifac        ,  169262,   67975, 0.402, 0.476, 2.839, 6.869, 11.841, 1.188'),
    '2RC'                  : ('final-results', 'trivial             , 2RC                 , mm_queueifac        ,   79989,   45811, 0.573, 2.099, 21.908, 29.800, 31.999, 6.256'),
    'RR'                   : ('final-results', 'trivial             , RR                  , mm_queueifac        ,   82915,   45143, 0.544, 1.994, 10.544, 30.389, 34.106, 5.450'),
    'random'               : ('final-results', 'trivial             , random              , mm_queueifac        ,  106674,   55066, 0.516, 1.341, 6.567, 25.617, 30.637, 4.438'),
    'theta-diff-plus'      : ('final-results', 'trivial             , theta-diff-plus     , mm_queueifac        ,  178509,   88480, 0.496, 0.395, 1.128, 5.121, 25.229, 1.146'),
    'ctl-simplify'         : ('final-results', 'trivial             , ctl-simplify        , mm_queueifac        ,  156466,   84059, 0.537, 0.591, 1.775, 10.743, 26.988, 2.015'),
    'equal-thetas-fast'    : ('final-results', 'trivial             , equal-thetas-fast   , mm_queueifac        ,  203000,   98491, 0.485, 0.222, 0.882, 2.162, 4.880, 0.413'),
    'theta-diff-plus-SQF'  : ('final-results', 'trivial             , theta-diff-plus-SQF , mm_queueifac        ,  202726,   90140, 0.445, 0.224, 1.203, 2.506, 4.472, 0.472'),
    'theta-diff-plus-fast' : ('final-results', 'trivial             , theta-diff-plus-fast, mm_queueifac        ,  199791,   87682, 0.439, 0.246, 1.334, 2.982, 4.738, 0.547'),
    'SRTF'                 : ('final-results', 'trivial             , SRTF                , mm_queueifac        ,  177320,  102330, 0.577, 0.404, 2.388, 4.680, 7.594, 0.888'),
    'equal-thetas-fast-mul': ('final-results', 'trivial             , equal-thetas-fast-mul, mm_queueifac        ,  201854,   99052, 0.491, 0.231, 0.900, 2.167, 14.795, 0.534'),
}

@mock.patch('base.SimulatorKernel.output')
def check_residue(lbAlgorithm, output):
    """
    Ensure the algorithm behaves exactly the same as it used to, in preparation for some intrusive refactoring.
    """
    with mock.patch('sys.argv', [
            './simulator.py',
            '--rc', 'mm_queueifac',
            '--lb', lbAlgorithm,
            '--scenario', 'scenarios/static_basic.py',
        ]):
        main()

    output.assert_called_with(*RESIDUE_TABLE[lbAlgorithm])

@nottest
def test_residue():
    for algorithm in LoadBalancer.ALGORITHMS:
        yield check_residue, algorithm
