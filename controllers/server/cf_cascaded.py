import numpy as np
import random as xxx_random # prevent accidental usage

from base.utils import *

def getName():
	return 'cc'

def addCommandLine(parser):
	parser.add_argument('--CCOuterPeriod',
		type = float,
		help = 'Specify the control period',
		default = 0.5,
	)
	parser.add_argument('--CCOuterK',
		type = float,
		help = 'Specify the outer proportional gain of the controller',
		default = 3.0,
	)
	parser.add_argument('--CCOuterTi',
		type = float,
		help = 'Specify the integral time constant',
		default = 0.5,
	)
	
	parser.add_argument('--CCShouldRunFF',
		type = float,
		help = '1 if feedforward should be used, 0 otherwise',
		default = 0,
	)

def parseCommandLine(_args):
	global args
	args = _args

def newInstance(sim, name):
	return MMReplicaController(sim, name, \
		args.CCOuterPeriod, args.CCOuterK, \
		args.CCOuterTi, args.CCShouldRunFF)

class MMReplicaController:
	def __init__(self, sim, name, period, outerK, \
		outerTi, shouldRunFF, seed = 1):
			
		## Outer loop parameters
		self.setpoint = 1.0
		self.error = 0.0
		self.controlPeriod = period 
		self.responseTime = 0.0
		self.percentile = 95
		self.outerK = outerK
		self.outerTi = outerTi
		self.integralPart = 0.0
		self.outerTr = 15.0
		self.feedback = 0.0
		self.feedforward = 0.0
		self.shouldRunFF = shouldRunFF
		
		## Inner loop parameters
		self.queueLength = 0
		self.queueLengthSetpoint = 0

		## All latencies measured during last control period (controller input)
		self.latestLatencies = []
		## Long latencies measured during last control period (controller input)
		self.latestLongLatencies = []
		## Short latencies measured during last control period (controller input)
		self.latestShortLatencies = []
		## nbr of arrived requests during control period
		self.nbrLatestArrivals = 0
		
		## Reference to simulator
		self.sim = sim
		if self.controlPeriod > 0:
			self.sim.add(0, self.runControlLoop)
		
		## Random number generator
		self.random = xxx_random.Random()
		self.random.seed(seed)

		## Controller ID for pretty-printing
		self.name = name
		
		## Estimated parameters
		self.qshat = 0.0
		self.that = 0.0
		self.qhat = 0.0
		self.pastQueues = []
		self.avgQueues = 0.0
		self.maxQueues = 0
		self.dimmerTuples = []
		self.expdimmers = 0.0
		self.estimatedArrivalRate = 0.0
		self.alpha = 1.0
		self.gihat = 1.0

	## Runs the outer periodical control loop that sets queue length setpoint
	def runControlLoop(self):
		
		if self.latestLatencies:
			
			if len(self.latestLongLatencies) > 0:
				oldError = self.error
				#self.responseTime = avg(self.latestLongLatencies) # avg long latency
				self.responseTime = np.percentile(self.latestLongLatencies, 95) # np 95 long latency
				#self.responseTime = avg(self.latestLatencies) # avg latencies
				#self.responseTime = max(self.latestLatencies) # max of all latencies
				self.error = self.setpoint - self.responseTime
				
				# Outer loop PI controller		
				proportionalPart = self.outerK * self.error
				prelFeedback = proportionalPart + self.integralPart
				
				# Update parameter estimates			
				self.updateOuterLoopEstimates()
				
				# Calculate feedforward if activated
				if self.shouldRunFF == 1:
					self.feedforward = self.setpoint * self.estimatedArrivalRate / (self.alpha*self.gihat)
				else:
					self.feedforward = 0.0
		
				# Saturate control signal
				feedbackMin = -1.0*self.feedforward
				self.feedback = max(prelFeedback, feedbackMin)
				
				# Calculate control signal
				self.queueLengthSetpoint = self.feedback + self.feedforward
				
							
				# Update controller integral state
				self.integralPart = self.integralPart + self.error * \
						(self.outerK * self.controlPeriod / self.outerTi) + \
						(self.controlPeriod / self.outerTr) * (self.feedback - prelFeedback)
					
		
		
		if len(self.latestLongLatencies) == 0:
			self.latestLongLatencies.append(0.0)
			
		if len(self.latestShortLatencies) == 0:
			self.latestShortLatencies.append(0.0)
		
		if len(self.latestLatencies) == 0:
			self.latestLatencies.append(0.0)
			
		if len(self.dimmerTuples) == 0:
			fakeTuple = -1,0, -1.0
			self.dimmerTuples.append(fakeTuple)
		
		dimmers = []
		
		for dt in self.dimmerTuples:
			dim = dt[1]
			dimmers.append(dim)
		
		# maxOrNan on the latencies rather than avg!
		# Report (the second to last one was previously self.dimmer)
		valuesToOutput = [ \
			self.sim.now, \
			self.responseTime, \
			np.percentile(self.latestLatencies, 95), \
			np.percentile(self.latestLongLatencies, 95), \
			np.percentile(self.latestShortLatencies, 95), \
			self.queueLength, \
			self.avgQueues, \
			self.queueLengthSetpoint, \
			self.nbrLatestArrivals, \
			self.estimatedArrivalRate, \
			avg(dimmers), \
			self.expdimmers, \
			self.feedback, \
			self.feedforward, \
			self.alpha, \
		]
		
		self.sim.output(self, ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))
				
		self.latestLatencies = []
		self.latestLongLatencies = []
		self.latestShortLatencies = []
		self.nbrLatestArrivals = 0
		
		# Re-run later
		self.sim.add(self.controlPeriod, self.runControlLoop)
		

	## Periodical estimations
	def updateOuterLoopEstimates(self):
		
		if (self.queueLengthSetpoint > 0.0):
			self.gihat = 0.9*self.gihat + 0.1*self.avgQueues/self.queueLengthSetpoint
			#gihat = 1.0
		
		self.estimatedArrivalRate = 0.5*self.estimatedArrivalRate + 0.5*self.nbrLatestArrivals/self.controlPeriod
		
		self.alpha = 0.99*self.alpha + 0.01*self.responseTime * self.estimatedArrivalRate / self.avgQueues

	
	## Inner loop control algorithm deciding execution of optional content	
	def withOptional(self, currentQueueLength):
		
		self.updateQueueMeasures(currentQueueLength)
		
		# Determine if optional content should be served
		if currentQueueLength > self.queueLengthSetpoint:
			dimmer = 0.0
		else:
			dimmer = 1.0
		
		self.updateDimmerMeasures(dimmer)
		
		return self.random.random() <= dimmer, dimmer


	def reportData(self, newArrival, responseTime, queueLength, timeY, timeN, optional):
		if newArrival:
			self.nbrLatestArrivals = self.nbrLatestArrivals + 1
		else:
			self.latestLatencies.append(responseTime)
			if (optional):
				self.latestLongLatencies.append(responseTime)
			else:
				self.latestShortLatencies.append(responseTime)
			self.queueLength = queueLength
	
	
	def updateQueueMeasures(self, currentQueueLength):
		queueMeasurement = self.sim.now, currentQueueLength	
		self.pastQueues.append(queueMeasurement)
		
		windowTime = self.controlPeriod + self.setpoint
		
		for qt in self.pastQueues:
			time = qt[0]
			if (self.sim.now - time > windowTime):
				self.pastQueues.remove(qt)
		
		self.avgQueues = 0.0
		queues = []	
		for index in range(len(self.pastQueues)):
			qt = self.pastQueues[index]
			queue = qt[1]
			queues.append(queue)
			self.avgQueues = (self.avgQueues*index + queue)/(index+1)
		
		self.maxQueues = max(queues)
		
	def updateDimmerMeasures(self, dimmer):
		alpha = 0.90
		self.expdimmers = alpha*self.expdimmers + (1-alpha)*dimmer
		
		dimmerTuple = self.sim.now, dimmer	
		self.dimmerTuples.append(dimmerTuple)
		
		windowTime = 100.0
		
		for dt in self.dimmerTuples:
			time = dt[0]
			if (self.sim.now - time > windowTime):
				self.dimmerTuples.remove(dt)
	
	def __str__(self):
		return self.name

