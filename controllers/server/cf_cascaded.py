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
		default = 4.0,
	)
	parser.add_argument('--CCOuterTi',
		type = float,
		help = 'Specify the integral time constant',
		default = 0.56,
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
		self.outerTr = 1.0
		self.feedback = 0.0
		self.feedforward = 0.0
		self.shouldRunFF = shouldRunFF
		
		## Inner loop parameters
		self.queueLength = 0
		self.queueLengthSetpoint = 0.0
		self.QueueLengthThreshold = 0.0
		self.v = 0.0

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
		self.pastDimmers = []
		self.expdimmers = 0.0
		self.estimatedArrivalRate = 25.0
		self.alpha = 1.0
		self.gihat = 1.0
		self.estimatedProcessGain = 0.05
		self.nominalProcessGain = 0.05

	## Runs the periodical control loop
	def runControlLoop(self):
		
		if self.latestLatencies:
			
			if len(self.latestLongLatencies) > 0:
				oldError = self.error
				self.responseTime = np.percentile(self.latestLongLatencies, 95) # np 95 long latency
				self.error = self.setpoint - self.responseTime
				
				# Update queue measurements
				self.updateQueueMeasures()
				
				# Update parameter estimates			
				self.updateOuterLoopEstimates()
				
				# Outer loop PI controller						
				factory = self.nominalProcessGain/self.estimatedProcessGain
					
				proportionalPart = factory*self.outerK * self.error
				prelFeedback = proportionalPart + self.integralPart
				
				
				# Calculate feedforward if activated
				if self.shouldRunFF == 1:
					self.feedforward = self.setpoint * self.estimatedArrivalRate / (self.alpha*self.gihat)
				else:
					self.feedforward = 0.0
		
				# Saturate control signal
				feedbackMin = -1.0*self.feedforward
				feedbackMax = self.estimatedArrivalRate - self.feedforward
				self.feedback = min(max(prelFeedback, feedbackMin), feedbackMax)
				
				
				# Calculate control signal
				self.queueLengthSetpoint = self.feedback + self.feedforward
						
				# Update outer controller integral state
				self.updateOuterState(factory, self.feedback, prelFeedback)
		
		
					
			
		# Inner P controller (in control signal v)
		queueError = self.queueLengthSetpoint - self.queueLength
		K_v = 2.0
		prelV = K_v*queueError
		
		# Saturation: No queue length thresholds below zero
		self.v = max(prelV, -1.0*self.queueLength)
		
		# Set threshold for actuation of control signal v
		self.QueueLengthThreshold = self.queueLength + self.v	
					
		
		if len(self.latestLongLatencies) == 0:
			self.latestLongLatencies.append(0.0)
			
		if len(self.latestShortLatencies) == 0:
			self.latestShortLatencies.append(0.0)
		
		if len(self.latestLatencies) == 0:
			self.latestLatencies.append(0.0)
			
		if len(self.pastDimmers) == 0:
			fakeTuple = -1,0, -1.0
			self.pastDimmers.append(fakeTuple)
		
		windowedAvgDimmers = self.updateDimmerMeasures()
		
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
			windowedAvgDimmers, \
			self.expdimmers, \
			self.feedback, \
			self.feedforward, \
			self.alpha, \
			self.estimatedProcessGain, \
			self.v, \
			self.QueueLengthThreshold, \
		]
		
		self.sim.output(self, ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))
				
		self.latestLatencies = []
		self.latestLongLatencies = []
		self.latestShortLatencies = []
		self.nbrLatestArrivals = 0
		
		# Re-run later
		self.sim.add(self.controlPeriod, self.runControlLoop)
		

	## Updates outer controller integral state (includes anti-windup)
	def updateOuterState(self, gain, u, v):
		self.integralPart = self.integralPart + self.error * \
						(gain*self.outerK * self.controlPeriod / self.outerTi) + \
						(self.controlPeriod / self.outerTr) * (u - v)
	
	## Periodical estimations
	def updateOuterLoopEstimates(self):
		
		if (self.queueLengthSetpoint > 0.0):
			self.gihat = 0.9*self.gihat + 0.1*self.avgQueues/self.queueLengthSetpoint
			#gihat = 1.0
		
		self.estimatedArrivalRate = 0.5*self.estimatedArrivalRate + 0.5*self.nbrLatestArrivals/self.controlPeriod
		
		self.alpha = 0.99*self.alpha + 0.01*self.responseTime * self.estimatedArrivalRate / self.avgQueues
		
		if (self.queueLengthSetpoint > 0.0):
			self.estimatedProcessGain = 0.90*self.estimatedProcessGain + 0.10*self.responseTime / self.queueLengthSetpoint
	
	
	## Inner loop actuator of control signal v deciding execution of optional content	
	def withOptional(self, currentQueueLength):
		
		self.saveQueueMeasures(currentQueueLength)
		
		# Determine if optional content should be served
		if currentQueueLength == 1:
			# Always serve optional content if queue is at minimum length
			dimmer = 1.0
		elif (currentQueueLength > self.QueueLengthThreshold):
			dimmer = 0.0
		else:
			dimmer = 1.0
		
		self.saveDimmerMeasures(dimmer)
		
		return self.random.random() <= dimmer, self.expdimmers


	def reportData(self, newArrival, responseTime, queueLength, timeY, timeN, optional):
		if newArrival:
			self.nbrLatestArrivals = self.nbrLatestArrivals + 1
		else:	
			self.latestLatencies.append(responseTime)
			if (optional):
				self.latestLongLatencies.append(responseTime)
				
				valuesToOutput = [ \
					responseTime, \
				]
				self.sim.output(str(self) + '-tommi', ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))
			
			else:
				self.latestShortLatencies.append(responseTime)
			self.queueLength = queueLength
	
	# Periodically updates the windowed dimmer average (used for estimates and plotting)
	def updateQueueMeasures(self):
		windowTime = self.controlPeriod + self.setpoint
		
		for qt in self.pastQueues:
			time = qt[0]
			if (self.sim.now - time > windowTime):
				self.pastQueues.remove(qt)
		
		queues = []		
		for qt in self.pastQueues:
			queue = qt[1]
			queues.append(queue)
		
		self.avgQueues = avg(queues)
		self.maxQueues = max(queues)
	
	
	# Stores the current queue length. Run in an event-triggered fashion.
	def saveQueueMeasures(self, currentQueueLength):
		queueMeasurement = self.sim.now, currentQueueLength	
		self.pastQueues.append(queueMeasurement)
	
	# Periodically updates the windowed dimmer average (only used for plotting atm)
	def updateDimmerMeasures(self):
		windowTime = 100.0
		
		for dt in self.pastDimmers:
			time = dt[0]
			if (self.sim.now - time > windowTime):
				self.pastDimmers.remove(dt)
		
		dimmers = []	
		for dt in self.pastDimmers:
			dim = dt[1]
			dimmers.append(dim)
		
		return avg(dimmers)
	
	# Stores the current dimmer value and updates expdimmers. Run in an event-triggered fashion.
	def saveDimmerMeasures(self, dimmer):
		alpha = 0.95
		self.expdimmers = alpha*self.expdimmers + (1-alpha)*dimmer
		
		dimmerTuple = self.sim.now, dimmer	
		self.pastDimmers.append(dimmerTuple)
	
	def __str__(self):
		return self.name

