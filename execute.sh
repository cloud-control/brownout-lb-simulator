#!/bin/bash

rm -rf results
mkdir -p results

#algs=( equal-thetas-fast SRTF random RR weighted-RR theta-diff theta-diff-plus theta-diff-plus-SQF optimization SQF SQF-plus FRF equal-thetas FRF-EWMA predictive 2RC ctl-simplify equal-thetas-SQF optim-SQF theta-diff-plus-fast)
algs=( equal-thetas equal-thetas-SQF SQF )

for algorithm in "${algs[@]}"
do
    mkdir -p results/${algorithm}
    ./simulator.py --algorithm ${algorithm} --outdir results/${algorithm} $@ &
done
wait

echo
echo "Results sorted by algorithm:"
tail -n1 -q results/*/sim-final-results.csv | sort

echo
echo "Results sorted by optional content:"
tail -n1 -q results/*/sim-final-results.csv | sort -t, -k4 -r | cut -d, -f1,2,4

echo
echo "Results sorted by 95th percentile response time:"
tail -n1 -q results/*/sim-final-results.csv | sort -t, -k7 -r | cut -d, -f1,2,7

echo
echo "Results sorted by 99th percentile response time:"
tail -n1 -q results/*/sim-final-results.csv | sort -t, -k8 -r | cut -d, -f1,2,8

echo
echo "Results sorted by maximum response time:"
tail -n1 -q results/*/sim-final-results.csv | sort -t, -k9 -r | cut -d, -f1,2,9

echo
echo "Results sorted by response time stddev"
tail -n1 -q results/*/sim-final-results.csv | sort -t, -k10 -r | cut -d, -f1,2,10

