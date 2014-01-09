#!/bin/bash

mkdir -p results

algs=( static theta-diff optimization SQF FRF equal-thetas FRF-EWMA predictive )

for algorithm in "${algs[@]}"
do
	mkdir -p results/${algorithm}
	./simulator.py algorithm ${algorithm}
	mv *.csv results/${algorithm}
done


