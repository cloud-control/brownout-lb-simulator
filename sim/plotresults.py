#!/usr/bin/env python
import fnmatch
import os
import numpy as np
from pylab import *

def main():
	replicas = 0
	for f in os.listdir('.'):
    		if fnmatch.fnmatch(f, 'sim-lb.csv'):
			data = np.genfromtxt(f, dtype=float, delimiter=',') 
		if fnmatch.fnmatch(f, 'sim-server*.csv'):
        		replicas += 1

	# parse data
	times = data[:,0]
	weights = data[:,1:replicas]
	dimmers = data[:,replicas+1:2*replicas]
	avg_latencies = data[:,2*replicas+1:3*replicas]
	max_latencies = data[:,3*replicas+1:4*replicas]
	total_requests = data[:,4*replicas+1]
	optional_requests = data[:,4*replicas+2]
	effective_weights = data[:,4*replicas+2:5*replicas+1]

	figure(1)
	plot(times, weights)
	title("Weights")
	figure(2)
	plot(times, dimmers)
	title("Dimmers")
	figure(3)
	plot(times, max_latencies)
	title("Max latencies")
	figure(4)
	plot(times, optional_requests/total_requests)
	title("Percentage recommendations")
	show()


if __name__ == "__main__":
	main()

