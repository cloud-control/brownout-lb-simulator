#!/bin/bash

mkdir -p results

algs=( weighted-RR theta-diff optimization SQF SQF-plus FRF equal-thetas equal-thetas-SQF optim-SQF FRF-EWMA predictive 2RC RR random theta-diff-plus ctl-simplify equal-thetas-fast theta-diff-plus-SQF theta-diff-plus-fast SRTF equal-thetas-fast-mul oracle )
algs=( equal-thetas theta-diff-plus weighted-RR SQF predictive optimization random RR FRF FRF-EWMA 2RC )

for algorithm in "${algs[@]}"
do
    mkdir -p results/${algorithm}
    ./simulator.py --algorithm ${algorithm} --outdir results/${algorithm} $@ &
    algo=$algorithm
done
wait

echo
echo "Results sorted by algorithm:"
cat results/*/sim-final-results.csv | sort

echo
echo "Results sorted by performance:"
cat results/*/sim-final-results.csv | sort -t, -k2 -r

algo=results/$algo
cols=`tail -n1 $algo/sim-lb.csv |cut -d, -f1-10000 --output-delimiter="
"|wc -l`
let n=($cols-3)/5
let c1=4\*$n+2
let c2=4\*$n+3

echo
echo "Results sorted by number of optional requests:"
(for algo in results/*; do
	printf "%-20s %10d %10d\n" \
		`echo $algo | cut -d/ -f2` \
		`tail -n1 $algo/sim-lb.csv | cut -d, -f$c1 | cut -d. -f1` \
		`tail -n1 $algo/sim-lb.csv | cut -d, -f$c2 | cut -d. -f1`;
done) | sort -rnk 3
