from __future__ import print_function

import mock
import shutil
import sys
import tempfile
from nose.tools import *

from simulator import main

@mock.patch('base.SimulatorKernel.output')
def test_main(_):
    with mock.patch('sys.argv', [
            './simulator.py',
            '--lb', 'SQF',
            ]):
        main()

@mock.patch('base.SimulatorKernel.output')
@raises(SystemExit)
def test_invalid_algorithm(_):
    with mock.patch('sys.argv', [
            './simulator.py',
            '--lb',
            'non-existant',
            ]):
        main()

@mock.patch('base.SimulatorKernel.output')
def test_autoscaler(_):
    with mock.patch('sys.argv', [
            './simulator.py',
            '--lb', 'SQF',
            '--rc', 'mm_queueifac',
            '--scenario', './scenarios/autoscaling-support.py',
            ]):
        main()

@nottest
def test_all():
    outdir = tempfile.mkdtemp()
    print('Using:', outdir, file = sys.stderr)
    with mock.patch('sys.argv', [
            './simulator.py',
            '--ac', 'ALL',
            '--rc', 'ALL',
            '--scenario', './scenarios/autoscaling-support.py',
            '--outdir', outdir
            ]):
        main()
    shutil.rmtree(outdir)
