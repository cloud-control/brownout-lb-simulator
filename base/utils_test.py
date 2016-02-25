import math
import random

from utils import *

def weightedChoice_test():
    assert weightedChoice([('a', 0.1), ('b', 0.9)], random.Random()) in ['a', 'b']
    assert weightedChoice([('a', 0.0), ('b', 1.0)], random.Random()) in ['b']
    assert weightedChoice([('a', 1.0), ('b', 0.0)], random.Random()) in ['a']

def avg_test():
    assert avg([1, 2, 3]) == 2
    assert math.isnan(avg([]))

def maxOrNan_test():
    assert maxOrNan([1, 2, 3, 1]) == 3
    assert math.isnan(maxOrNan([]))

def normalize_test():
    assert normalize([]) == []
    assert normalize([1, 2, 3]) == [1.0/6, 2.0/6, 3.0/6]
    assert normalize([0.5]) == [1.0]
    assert math.isnan(normalize([0, 0])[0])
