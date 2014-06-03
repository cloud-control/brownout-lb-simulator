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
tail -n1 -q results/*/sim-final-results.csv | sort -t, -nk4 -r | cut -d, -f1,2,4,5

echo
echo "Results sorted by average response time:"
tail -n1 -q results/*/sim-final-results.csv | sort -t, -nk6 | cut -d, -f1,2,6

echo
echo "Results sorted by 95th percentile response time:"
tail -n1 -q results/*/sim-final-results.csv | sort -t, -nk7 | cut -d, -f1,2,7

echo
echo "Results sorted by 99th percentile response time:"
tail -n1 -q results/*/sim-final-results.csv | sort -t, -nk8 | cut -d, -f1,2,8

echo
echo "Results sorted by maximum response time:"
tail -n1 -q results/*/sim-final-results.csv | sort -t, -nk9 | cut -d, -f1,2,9

echo
echo "Results sorted by response time stddev"
tail -n1 -q results/*/sim-final-results.csv | sort -t, -nk10 | cut -d, -f1,2,10

