#!/usr/bin/env python
from __future__ import division

import random
import sys

#lam = int(sys.argv[1])
#theta = float(sys.argv[2])
#muM=int(sys.argv[3])
#muO=int(sys.argv[4])
#tend = float(sys.argv[5])

lam = 15
theta = 0.5
muM = 500
muO = 10
tend = 10000

def get_proc():
  withOptional = random.random() < theta
  if withOptional:
    return random.expovariate(muO)
  else:
    return random.expovariate(muM)
    
q = []
next_arrival = random.expovariate(lam)
next_departure = -1

nm = 0
sm = 0
serviceTimeSum = 0
serviceTimeNum = 0

t = 0
while t < tend:
  if next_departure == -1 or next_arrival <= next_departure:
    # Arrival
    t = next_arrival
    
    next_arrival = next_arrival + random.expovariate(lam)
    q.insert(0, t)
    if next_departure == -1:
      proc = get_proc()
      serviceTimeSum += proc
      serviceTimeNum += 1
      next_departure = t + proc
      
  else:
    # Departure
    t = next_departure
    
    arr = q.pop()
    
    rt = t - arr
    nm = nm + 1
    sm = sm + rt
    
    if len(q) == 0:
      next_departure = -1
    else:
      proc = get_proc()
      next_departure = t + proc
      serviceTimeSum += proc
      serviceTimeNum += 1

mueff = 1 / ((1-theta)/muM + theta/muO)
print "Service rate: ", serviceTimeNum / serviceTimeSum, "estimated through harmonic mean", mueff
print("Mean %f, according to harmonic mean %f"%(sm/nm, 1 / (mueff - lam)))
