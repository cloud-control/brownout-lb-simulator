#!/usr/bin/env python
from __future__ import division

import random
import sys
import numpy as np

#lam = int(sys.argv[1])
#theta = float(sys.argv[2])
#muM=int(sys.argv[3])
#muO=int(sys.argv[4])
#tend = float(sys.argv[5])

policy = "fifo"
#policy = "ps"

print "theta\tmeasurd\tM/H2/1\tM/H2/1-PS"
for theta in np.arange(0, 1.1, .1):
  lam = 9
  muM = 1000
  muO = 10
  tend = 10000

  nm = 0
  sm = 0
  serviceTimeSum = 0
  serviceTimeNum = 0

  def get_proc():
    global serviceTimeSum, serviceTimeNum
    
    withOptional = random.random() < theta
    if withOptional:
      proc = random.expovariate(muO)
    else:
      proc = random.expovariate(muM)
    
    serviceTimeNum += 1
    serviceTimeSum += proc
    
    return proc
    
  lastPsT = 0
  currentWork = 0
  def update_ps():
    global lastPsT, currentWork
    
    if len(q) > 0:
      dt = t - lastPsT
      dwork = dt/len(q)
      currentWork += dwork
      
      # Wrap to keep precision
      if currentWork >= 1000:
        currentWork -= 1000
        for job in q:
          job[1] -= 1000
      
    lastPsT = t
    
  q = []
  next_arrival = random.expovariate(lam)
  next_departure = -1

  t = 0
  while t < tend:
    if next_departure == -1 or next_arrival <= next_departure:
      # Arrival
      t = next_arrival
      
      next_arrival = next_arrival + random.expovariate(lam)
      if policy == "fifo":
        q.insert(0, t)
        
        if next_departure == -1:
          proc = get_proc()
          next_departure = t + proc
      
      elif policy == "ps":
        update_ps()
        
        proc = get_proc()
        q.append([t, currentWork+proc])
        q.sort(key=lambda x: x[1])
        
        next_departure = t + (q[0][1]-currentWork)*len(q)
          
      else:
        raise RuntimeError("Unknown policy \"%s\""%policy)
      
    else:
      # Departure
      t = next_departure
      
      if policy == "fifo":
        arrivaltime = q.pop()
      
        if len(q) == 0:
          next_departure = -1
        else:
          proc = get_proc()
          next_departure = t + proc

      elif policy == "ps":
        update_ps()
        
        job = q.pop(0)
        arrivaltime = job[0]
        
        if len(q) == 0:
          next_departure = -1
        else:
          next_departure = t + (q[0][1]-currentWork)*len(q)

      else:
        raise RuntimeError("Unknown policy \"%s\""%policy)

      rt = t - arrivaltime
      nm += 1
      sm += rt
      
  m = muM
  M = muO
  eS = theta / M + (1 - theta) / m
  varS = 2 * theta / (M ** 2) + 2 * (1 - theta) / (m ** 2) - eS ** 2
  rho = lam * eS
  mu = 1 / eS
  avgRT = (rho + lam * mu * varS) / (2 * (mu - lam)) + 1/mu

  mueff = 1/(theta / muO + (1-theta) / muM)
  old = 1/(mueff - lam)

  print "%.1f\t%.3f\t%.3f\t%.3f"%(theta, sm/nm, avgRT, old)
  


