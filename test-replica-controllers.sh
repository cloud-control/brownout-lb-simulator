#!/bin/bash

rm -rf results
mkdir -p results

for algoFilename in rcf_*.py; do
	algorithm=`basename $algoFilename .py | cut -c5-`
	mkdir -p results/${algorithm}
	./simulator.py --rc ${algorithm} --outdir results/${algorithm} $@ &
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
tail -n1 -q results/*/sim-final-results.csv | sort -t, -k7 | cut -d, -f1,2,7

echo
echo "Results sorted by 99th percentile response time:"
tail -n1 -q results/*/sim-final-results.csv | sort -t, -k8 | cut -d, -f1,2,8

echo
echo "Results sorted by maximum response time:"
tail -n1 -q results/*/sim-final-results.csv | sort -t, -k9 | cut -d, -f1,2,9

echo
echo "Results sorted by response time stddev"
tail -n1 -q results/*/sim-final-results.csv | sort -t, -k10 | cut -d, -f1,2,10

