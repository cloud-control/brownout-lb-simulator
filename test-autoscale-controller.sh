#!/bin/bash
mkdir -p results/test-autoscaling-controller
./simulator.py --algorithm SQF --rc mm_queueifac --scenario ./scenarios/autoscaling-support.py --outdir results/test-autoscaling-controller
