#!/bin/bash

mkdir -p results

algs=( random RR weighted-RR theta-diff optimization SQF FRF equal-thetas FRF-EWMA predictive 2RC )

for algorithm in "${algs[@]}"
do
	mkdir -p results/${algorithm}
	./simulator.py --algorithm ${algorithm} --outdir results/${algorithm} $@ &
done
wait

echo
echo "Results sorted by algorithm:"
cat results/*/sim-final-results.csv | sort

echo
echo "Results sorted by performance:"
cat results/*/sim-final-results.csv | sort -t, -k2 -r
