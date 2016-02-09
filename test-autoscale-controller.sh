#!/bin/bash
mkdir -p results/test-autoscaling-controller
./simulator.py --algorithm SQF --scenario ./scenarios/autoscaling-support.py --outdir results/test-autoscaling-controller
