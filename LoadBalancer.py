from __future__ import division

#from cvxopt import solvers, matrix, spdiag, log
#import cvxopt
import math
import numpy as np

from Request import *
from utils import *

## Simulates a load-balancer.
# The load-balancer is assumed to take zero time for its decisions.
class LoadBalancer:
	## Constructor.
	# @param sim Simulator to attach to
	# @param controlPeriod control period
	# @param initialTheta initial dimmer value to consider before receiving any
	# replies from a server
	def __init__(self, sim, controlPeriod = 1, initialTheta = 0.5):
		## control period (control parameter)
		self.controlPeriod = controlPeriod # second
		## initial value of measured theta (control initialization parameter)
		self.initialTheta = initialTheta
		## what algorithm to use
		self.algorithm = 'theta-diff'

		## Simulator to which the load-balancer is attached
		self.sim = sim
		## list of back-end servers to which requests can be directed
		self.backends = []
		## weights determining how to load-balance requests (control output)
		self.weights = []
		## last deviation of theta from the average (for equal-thetas)
		self.lastThetaErrors = []
		## dimmer values measured during the previous control period (control input)
		self.lastThetas = []
		## dimmer values measured during before previous control period
		# (control input)
		self.lastLastThetas = []
		## latencies measured during last control period (metric)
		self.lastLatencies = []
		self.lastLastLatencies = []
		## queue length of each replica (control input for SQF algorithm)
		self.queueLengths = []
		self.lastQueueLengths = []
		## queue length offset for equal-thetas-SQF
		self.queueOffsets = []
		## number of requests, with or without optional content, served since
		# the load-balancer came online (metric)
		self.numRequests = 0
		self.lastNumRequests = 0
		## number of requests, with optional content, served since the
		# load-balancer came online (metric)
		self.numRequestsWithOptional = 0
		## number of requests served by each replica (metric).
		self.numRequestsPerReplica = []
		## number of requests served by each replica before the last control period (metric).
		self.numLastRequestsPerReplica = []
		self.iteration = 1
		## average response time of each replica (control input for FRF-EWMA algorithm)
		self.ewmaResponseTime = []
		## number of sample to use for computing average response time (parameter for FRF-EWMA algorithm)
		self.ewmaNumSamples = 10
		## for the ctl-simplify algorithm
		self.ctlRlsP = []
		self.ctlAlpha = []
		## time when last event-driven control decision was taken
		self.lastDecision = 0
		
		# suppress output of cvxopt solver
		#solvers.options['show_progress'] = False

		# Launch control loop
		self.sim.add(0, self.runControlLoop)

	## Adds a new back-end server and initializes decision variables.
	# @param backend the server to add
	def addBackend(self, backend):
		self.backends.append(backend)
		self.lastThetaErrors.append(0)
		self.lastThetas.append(self.initialTheta) # to be updated at onComplete
		self.lastLastThetas.append(self.initialTheta) # to be updated at onComplete
		self.lastLatencies.append([]) # to be updated at onComplete
		self.lastLastLatencies.append([])
		self.queueLengths.append(0) # to be updated in request and onComplete
		self.lastQueueLengths.append(0)
		self.queueOffsets.append(0)
		self.numRequestsPerReplica.append(0) # to be updated in request
		self.numLastRequestsPerReplica.append(0) # to be updated in runControlLoop
		self.ewmaResponseTime.append(0) # to be updated in onComplete
		## for ctl-simplify
		self.ctlRlsP.append(1000)
		self.ctlAlpha.append(1)

		self.weights = [ 1.0 / len(self.backends) ] * len(self.backends)

	## Handles a request.
	# @param request the request to handle
	def request(self, request):
		#self.sim.log(self, "Got request {0}", request)
		request.arrival = self.sim.now
		if self.algorithm in [ 'weighted-RR', 'theta-diff', 'theta-diff-plus', 'equal-thetas', 'optimization', 'ctl-simplify' ]:
			request.chosenBackendIndex = \
				weightedChoice(zip(range(0, len(self.backends)), self.weights))
		elif self.algorithm == 'equal-thetas-SQF' or self.algorithm == 'equal-thetas-fast':
			# Update controller in the -fast version
			if self.algorithm == 'equal-thetas-fast':
				dt = self.sim.now - self.lastDecision
				if dt > 1: dt = 1
				for i in range(0,len(self.backends)):
					# Gain
					gamma = .1 * dt
					gammaTr = .01 * dt
					
					# Calculate the negative deviation from the average
					e = self.lastThetas[i] - avg(self.lastThetas)
					# Integrate the negative deviation from the average
					self.queueOffsets[i] += gamma * e # + Kp * (e - self.lastThetaErrors[i])
					self.lastThetaErrors[i] = e
				self.lastDecision = self.sim.now
					
			# To prevent starvation, choose a random empty server..
			empty_servers = [i for i in range(0, len(self.queueLengths)) \
				if self.queueLengths[i] == 0]
			
			if len(empty_servers) > 0:
				request.chosenBackendIndex = random.choice(empty_servers)
			else:
				# ...or choose replica with shortest (queue + queueOffset)
				request.chosenBackendIndex = \
					min(range(0, len(self.queueLengths)), \
					key = lambda i: self.queueLengths[i]-self.queueOffsets[i])

		elif self.algorithm == 'theta-diff-plus-SQF':
			# choose replica with shortest (queue + queueOffset)
			request.chosenBackendIndex = \
				min(range(0, len(self.queueLengths)), \
				key = lambda i: self.queueLengths[i]-self.queueOffsets[i])
			pass
		elif self.algorithm == 'optim-SQF':
			request.chosenBackendIndex = \
				min(range(0, len(self.queueLengths)), \
				key = lambda i: self.queueLengths[i]-self.queueOffsets[i])
		elif self.algorithm == 'random':
			# round robin
			request.chosenBackendIndex = \
				random.choice(range(0, len(self.backends)))
		elif self.algorithm == 'RR':
			# round robin
			request.chosenBackendIndex = \
				(self.numRequests % len(self.backends)) - 1
		elif self.algorithm == 'SQF':
			# choose replica with shortest queue
			request.chosenBackendIndex = \
				min(range(0, len(self.queueLengths)), \
				key = lambda i: self.queueLengths[i])
		elif self.algorithm == 'SQF-plus':
			# choose replica with shortest queue
			minIndices = [i for i, x in enumerate(self.queueLengths) if x == min(self.queueLengths)]
			if len(minIndices) == 1:
				request.chosenBackendIndex = minIndices[0]
			else:
				dimmers = [self.lastThetas[i] for i in minIndices]
				maxDimmerIndex = dimmers.index(max(dimmers))
				request.chosenBackendIndex = minIndices[maxDimmerIndex]
		elif self.algorithm == '2RC':
			maxlat = [max(x) if x else 0 for x in self.lastLatencies]
			if len(self.backends) == 1:
				request.chosenBackendIndex = 0
			# randomly select two backends and send it to the one with lowest latency
			else:
				backends = set(range(0, len(self.backends)))
				randomlychosen = random.sample(backends, 2)
				if maxlat[randomlychosen[0]] > maxlat[randomlychosen[1]]:
					request.chosenBackendIndex = randomlychosen[1]
				else:
					request.chosenBackendIndex = randomlychosen[0]
		elif self.algorithm == 'FRF':
			# choose replica with minimum latency
			maxlat = [max(x) if x else 0 for x in self.lastLatencies]
			request.chosenBackendIndex = \
				maxlat.index(min(maxlat))
		elif self.algorithm == 'FRF-EWMA':
			# choose replica with minimum EWMA latency
			#self.sim.log(self, "EWMA RT {0}", self.ewmaResponseTime)
			request.chosenBackendIndex = \
				min(range(0, len(self.backends)), \
				key = lambda i: self.ewmaResponseTime[i])
		elif self.algorithm == 'predictive':
			maxlat = np.array([max(x) if x else 0 for x in self.lastLatencies])
			maxlatLast = np.array([max(x) if x else 0 for x in self.lastLastLatencies])
			wlat = 0.2
			wqueue = 0.8
			points = wlat*(maxlat - maxlatLast) + wqueue*(np.array(self.queueLengths) - np.array(self.lastQueueLengths))
			# choose replica with shortest queue
			request.chosenBackendIndex = \
				min(range(0, len(points)), \
				key = lambda i: points[i])
		elif self.algorithm == "SRTF":
			# choose replica with shortest "time" queue
			#request.chosenBackendIndex = \
			#	min(range(0, len(self.backends)), \
			#	key = lambda i: sum([r.remainingTime if hasattr(r, 'remainingTime') else 0 for r in self.backends[i].activeRequests]))
			request.chosenBackendIndex = \
				min(range(0, len(self.queueLengths)), \
				key = lambda i: self.queueLengths[i] * (self.backends[i].serviceTimeY * self.lastThetas[i] + self.backends[i].serviceTimeN * (1 - self.lastThetas[i])))
		elif self.algorithm == 'theta-diff-plus-fast':
			dt = self.sim.now - self.lastDecision
			if dt > 1: dt = 1

			for i in range(0,len(self.backends)):
				# Gain
				Kp = 0.25
				Ti = 5.0
				gammaTr = .01

				# PI control law
				e = self.lastThetas[i] - self.lastLastThetas[i]
				self.queueOffsets[i] += (Kp * e + (Kp/Ti) * self.lastThetas[i]) * dt

				# Anti-windup
				self.queueOffsets[i] -= gammaTr * (self.queueOffsets[i] - self.queueLengths[i]) * dt
				self.lastThetaErrors[i] = e

			self.lastDecision = self.sim.now
			
			# choose replica with shortest (queue + queueOffset)
			request.chosenBackendIndex = \
				min(range(0, len(self.queueLengths)), \
				key = lambda i: self.queueLengths[i]-self.queueOffsets[i])
		else:
			raise Exception("Unknown load-balancing algorithm " + self.algorithm)
			
		newRequest = Request()
		newRequest.originalRequest = request
		newRequest.onCompleted = lambda: self.onCompleted(newRequest)
		#self.sim.log(self, "Directed request to {0}", request.chosenBackendIndex)
		self.queueLengths[request.chosenBackendIndex] += 1
		self.numRequestsPerReplica[request.chosenBackendIndex] += 1
		self.backends[request.chosenBackendIndex].request(newRequest)

	## Handles request completion.
	# Stores piggybacked dimmer values and calls orginator's onCompleted() 
	def onCompleted(self, request):
		# "Decapsulate"
		self.numRequests += 1
		if request.withOptional:
			self.numRequestsWithOptional += 1
		theta = request.theta
		request.originalRequest.withOptional = request.withOptional
		request = request.originalRequest

		# Store stats
		request.completion = self.sim.now
		self.lastThetas[request.chosenBackendIndex] = theta
		self.lastLatencies[request.chosenBackendIndex].\
			append(request.completion - request.arrival)
		self.queueLengths[request.chosenBackendIndex] -= 1
		ewmaAlpha = 2 / (self.ewmaNumSamples + 1)
		self.ewmaResponseTime[request.chosenBackendIndex] = \
			ewmaAlpha * (request.completion - request.arrival) + \
			(1 - ewmaAlpha) * self.ewmaResponseTime[request.chosenBackendIndex]
	
		# Call original onCompleted
		request.onCompleted()

	## Run control loop.
	# Takes as input the dimmers and computes new weights. Also outputs
	# CVS-formatted statistics through the Simulator's output routine.
	def runControlLoop(self):
		if self.algorithm == 'weighted-RR':
			# Nothing to do here
			pass
		elif (self.algorithm == 'optimization' or self.algorithm == 'optim-SQF'):
			setpoint = 1
			arrivalRate = float(self.numRequests - self.lastNumRequests) / float(self.controlPeriod)
			#arrivalRate = 50
			#arrivalRate = 20
			# TODO: we have to substitute these vectors (mu and M) 
			# with estimations of their values
			mutmp = matrix(np.zeros((len(self.weights), 1)))
			Mtmp = matrix(np.zeros((len(self.weights), 1)))
			for i in range(0, len(self.weights)):
				mutmp[i] = self.backends[i].serviceTimeN
				Mtmp[i] = self.backends[i].serviceTimeY
			mu = cvxopt.div(1,mutmp)
			M = cvxopt.div(1,Mtmp)
			A = matrix(np.ones((1, len(self.weights)))) # A and b are constraints for the sum of weights to be 1.0
			b = matrix(1.0, (1,1), 'd')
			m, n = A.size
			# intermediate quantities for optimization
			intA = cvxopt.mul(M,mu)*setpoint - M
			intB = M*arrivalRate*setpoint
			intC = mu - M
			intD = (mu - M)*arrivalRate*setpoint 
			# inequality constraints
			G = matrix(0.0, (3*len(self.weights), len(self.weights)), 'd')
			for i in range(0, len(self.weights)):
				G[i,i] = -1.0 # constraints for nonnegativity of weights
				G[len(self.weights) + i, i] = 1.0 # constrain that lower bound on optimal dimmers is 0
				G[2*len(self.weights) + i, i] = -1.0 # constrain that upper bound on optimal dimmers is 1
			h = matrix(0.0, (3*len(self.weights), 1), 'd')
			for i in range(0, len(self.weights)):
				if intB[i] == 0: # avoid initial corner case
					h[len(self.weights) + i, 0] = 1
					h[2*len(self.weights) + i, 0] = 1
				else:
					h[len(self.weights) + i, 0] = intA[i] / intB[i] # for dimmers greater than 0
					h[2*len(self.weights) + i, 0] = (intC[i] - intA[i]) / (intD[i] + intB[i]) # for dimmers lower than 1
			def F(x=None, z=None):
				if x is None: return 0, matrix(1.0, (n, 1))
				if min(x) <= 0.0: return None
				# function that we want to minimize
				f = -sum(cvxopt.mul(x, cvxopt.div(intA-cvxopt.mul(intB,x), intC+cvxopt.mul(intD,x))))
				Df = -(cvxopt.div((cvxopt.mul(intA,intC) -  \
                                     2*cvxopt.mul(intB,cvxopt.mul(intC,x))-cvxopt.mul(intB,cvxopt.mul(intD,(x**2)))),\
				     ((intC+cvxopt.mul(intD,x))**2))).T
				if z is None: return f, Df
				H = spdiag((
					cvxopt.div(2*cvxopt.mul(intA,cvxopt.mul(intC,intD)), (intC+cvxopt.mul(intD,x))**3) + \
					cvxopt.div(2*cvxopt.mul(intB,(intC**2)), (intC+cvxopt.mul(intD,x))**3)
					))
				return f, Df, H
			#print(-h[2*len(self.weights):3*len(self.weights)])
			lower_tmp = [i for i in -h[2*len(self.weights):3*len(self.weights)] if i > 0]
			lower = sum(lower_tmp)
			#print(lower)
			if lower < 1.0: # if lower > 1 the servers are underloaded!
				#print(self.sim.now, arrivalRate)
				solution = solvers.cp(F, G, h, A=A, b=b)['x']
				self.weights = list(solution)
				#print(self.weights)
			else:
				rest = 1.0
				weights_tmp = matrix(0.0, (len(self.weights),1),'d')
				for i in range(0, len(self.weights)):
					if -h[2*len(self.weights)+i] < rest:
						weights_tmp[i,0] = -h[2*len(self.weights)+i]
						rest = rest + h[2*len(self.weights)+i]
						#print(rest)
					else:
						weights_tmp[i,0] = rest
						break
				#print(weights_tmp)
				self.weights = list(weights_tmp)
				#print(self.weights)
			for i in range(0,len(self.backends)):
				dim = min(1,(intA[i,0]-intB[i,0]*self.weights[i])/(intC[i,0]+intD[i,0]*self.weights[i]))
				mueff = 1/(dim/M[i]+(1-dim)/mu[i])
				self.queueOffsets[i] = arrivalRate*self.weights[i]/(mueff-arrivalRate*self.weights[i])
				#print(self.queueOffsets[i])
			x = matrix(self.weights)
			self.sim.output('optimizer', ','.join(map(str, [ self.sim.now ] + \
				list(cvxopt.div(intA-cvxopt.mul(intB,x), intC+cvxopt.mul(intD,x))))))
		elif self.algorithm == 'theta-diff':
			modifiedLastLastThetas = self.lastLastThetas # used to do the quick fix later
			# (by Martina:) a quick and dirty fix for this behavior that when the dimmer
			# is kept to 1 we are not doing a good job
			for i in range(0,len(self.lastThetas)):
				if (self.lastThetas[i] == 1 and self.lastLastThetas[i] == 1):
					modifiedLastLastThetas[i] = 0.99
			# end of the quick fix
			gain = 0.25
			self.weights = [ max(x[0] + gain*(x[1] - x[2]), 0.01) for x in \
				zip(self.weights, self.lastThetas, modifiedLastLastThetas) ]
			preNormalizedSumOfWeights = sum(self.weights)
			self.weights = [ x / preNormalizedSumOfWeights for x in self.weights ]
		elif self.algorithm == 'theta-diff-plus': 
			Kp = 0.5
			Ti = 5.0 
			self.weights = [ max(x[0] * (1 + Kp * (x[1] - x[2]) + (Kp/Ti) * x[1]), 0.01) for x in \
                            zip(self.weights, self.lastThetas, self.lastLastThetas) ]
			preNormalizedSumOfWeights = sum(self.weights)
			self.weights = [ x / preNormalizedSumOfWeights for x in self.weights ]
		elif self.algorithm == 'FRF-EWMA':
			# slowly forget response times
			ewmaAlpha = 2 / (self.ewmaNumSamples + 1)
			for i in range(0, len(self.backends)):
				self.ewmaResponseTime[i] *= (1 - ewmaAlpha)
		elif self.algorithm == 'predictive':
			# preditctive is not dynamic
			pass
		elif self.algorithm == 'theta-diff-plus-SQF':
			for i in range(0,len(self.backends)):
				# Gain
				Kp = 0.25
				Ti = 5.0
				gammaTr = .01

				# PI control law
				e = self.lastThetas[i] - self.lastLastThetas[i]
				self.queueOffsets[i] += Kp * e + (Kp/Ti) * self.lastThetas[i]

				# Anti-windup
				self.queueOffsets[i] -= gammaTr * (self.queueOffsets[i] - self.queueLengths[i])
				self.lastThetaErrors[i] = e
		elif self.algorithm == 'equal-thetas-SQF':
			for i in range(0,len(self.backends)):
				# Gain
				gamma = .1
				gammaTr = .01
				
				# Calculate the negative deviation from the average
				e = self.lastThetas[i] - avg(self.lastThetas)
				# Integrate the negative deviation from the average
				self.queueOffsets[i] += gamma * e # + Kp * (e - self.lastThetaErrors[i])
				self.lastThetaErrors[i] = e
		elif self.algorithm == 'equal-thetas':
			for i in range(0,len(self.backends)):
				# This code was meant to adjust the gain so that the weights of weak servers
				# react faster, since their response times react faster to changing loads.
				# Doesn't work... Yet.
				#theta = self.lastThetas[i]
				#muY = self.backends[i].serviceTimeY
				#muN = self.backends[i].serviceTimeN
				#mueff = 1/(theta/muY + (1-theta)/muN)
				#gamma = 6/mueff
				
				# Gain
				gamma = self.equal_theta_gain
				
				# Calculate the negative deviation from the average
				e = self.lastThetas[i] - avg(self.lastThetas)
				# Integrate the negative deviation from the average
				self.weights[i] += gamma * e # + Kp * (e - self.lastThetaErrors[i])
				self.lastThetaErrors[i] = e

				# Bound
				if self.weights[i] < 0.01:
					self.weights[i] = 0.01
			
			# Normalize
			weightSum = sum(self.weights)
			for i in range(0,len(self.backends)):
				self.weights[i] = self.weights[i] / weightSum
		elif self.algorithm == 'ctl-simplify':
			p = 0.99
			rlsForgetting = 0.99
			# RLS for alpha
			a = [ x[0]*x[1] \
				  for x in zip(self.ctlRlsP,self.weights) ]
			g = [ 1 / (x[0]*x[1] + rlsForgetting) \
			      for x in zip(self.weights,a) ]
			k = [ x[0]*x[1] \
				  for x in zip(g,a)]
			e = [ x[0] - x[1]*x[2]\
				  for x in zip(self.queueLengths,self.weights,self.ctlAlpha)]
			self.ctlAlpha = [ min(x[0] + x[1]*x[2],1.0)\
							  for x in zip(self.ctlAlpha,k,e)]
			self.ctlRlsP  = [ (x[0] - x[1] * x[2]*x[2]) / rlsForgetting \
							  for x in zip(self.ctlRlsP,g,a)]
						
			l = (self.numRequests - self.lastNumRequests) / self.controlPeriod
			xo = -10.0 # desired queue length
			if l == 0:
				for i in range(0,len(self.backends)):
					self.weights[i] = 1.0/len(self.backends)
			else:
				self.weights = [ max(x[0] + ((1-p)/l)* x[2] * (xo -x[1]) \
						- (1-p)/l* (xo - x[3]), 0.01) for x in \
						zip(self.weights, self.queueLengths, self.ctlAlpha, self.lastQueueLengths) ]
			# Normalize
			for i in range(0,len(self.backends)):
				self.weights[i] = self.weights[i] / sum(self.weights)
		# Other algorithms are not dynamic

		self.lastNumRequests = self.numRequests
		self.iteration += 1
		self.sim.add(self.controlPeriod, self.runControlLoop)

		# Compute effective weights
		effectiveWeights = [ self.numRequestsPerReplica[i] - self.numLastRequestsPerReplica[i] \
			for i in range(0,len(self.backends)) ]
		effectiveWeights = normalize(effectiveWeights)

		# Output the offsets as weights to enable plotting and stuff
		if self.algorithm == 'equal-thetas-SQF' or self.algorithm == 'equal-thetas-fast':
			self.weights = self.queueOffsets

		# Output the offsets as weights to enable plotting and stuff
		if self.algorithm == 'theta-diff-plus-SQF':
			self.weights = self.queueOffsets
			
		valuesToOutput = [ self.sim.now ] + self.weights + self.lastThetas + \
			[ avg(latencies) for latencies in self.lastLatencies ] + \
			[ max(latencies + [0]) for latencies in self.lastLatencies ] + \
			[ self.numRequests, self.numRequestsWithOptional ] + \
			effectiveWeights
		self.sim.output(self, ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))
		
		self.lastQueueLengths = self.queueLengths
		self.lastLastThetas = self.lastThetas[:]
		self.lastLastLatencies = self.lastLatencies
		self.lastLatencies = [ [] for _ in self.backends ]
		self.numLastRequestsPerReplica = self.numRequestsPerReplica[:]

	## Pretty-print load-balancer's name.
	def __str__(self):
		return "lb"

