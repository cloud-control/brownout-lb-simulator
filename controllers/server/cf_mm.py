import numpy as np
import random as xxx_random # prevent accidental usage

from base.utils import *

def getName():
	return 'mm'

def addCommandLine(parser):
	parser.add_argument('--rcMmInitialDimmer',
		type = float,
		help = 'Specify the initial dimmer for the MM controller',
		default = 0.5,
	)
	parser.add_argument('--rcMmPeriod',
		type = float,
		help = 'Specify the control period for the MM controller',
		default = 0.5,
	)
	parser.add_argument('--rcMmPole',
		type = float,
		help = 'Specify the pole for the MM controller',
		default = 0.9,
	)
	parser.add_argument('--rcMmRlsForgetting',
		type = float,
		help = 'Specify the RLS forgetting factor for the MM controller',
		default = 0.95,
	)

def parseCommandLine(_args):
	global args
	args = _args

def newInstance(sim, name):
	return MMReplicaController(sim, name, \
		args.rcMmInitialDimmer, args.rcPercentile, \
		args.rcMmPeriod, args.rcMmPole, args.rcMmRlsForgetting, \
		args.rcSetpoint)

class MMReplicaController:
	def __init__(self, sim, name, initialDimmer, percentile, period, pole, \
		rlsForgetting, setpoint, seed = 1):
		## control period (controller parameter)
		self.controlPeriod = period # second
		## setpoint (controller parameter)
		self.setpoint = setpoint
		## percentile to control (controller parameter)
		self.percentile = percentile
		## initialization for the RLS estimator (controller variable)
		self.rlsP = 1000
		## RLS forgetting factor (controller parameter)
		self.rlsForgetting = rlsForgetting
		## Current alpha (controller variable)
		self.alpha = 1
		## Pole (controller parameter)
		self.pole = pole
		## latencies measured during last control period (controller input)
		self.latestLatencies = []
		## dimmer value (controller output)
		self.dimmer = initialDimmer

		## Reference to simulator
		self.sim = sim
		if self.controlPeriod > 0:
			self.sim.add(0, self.runControlLoop)
		
		## Random number generator
		self.random = xxx_random.Random()
		self.random.seed(seed)

		## Controller ID for pretty-printing
		self.name = name
		
		## Added parameters
		self.latestLongLatencies = []
		self.latestShortLatencies = []
		self.queueLength = 0
		self.nbrLatestArrivals = 0.0
		self.responseTime = 0.0
		self.pastResponseTimesTuples = []
		self.pastResponseTimes = []
		self.pastQueues = []
		self.avgQueues = 0.0
		self.expdimmers = 0.0
		self.dimmerTuples = []


	## Runs the control loop.
	# Basically retrieves self.lastestLatencies and computes a new self.dimmer.
	# Ask Martina for details. :P
	def runControlLoop(self):
		output_dimmer = float('nan')
	
		if self.latestLatencies:
			if len(self.latestLatencies) > 0:
				# Possible choices: max or avg latency control
				#serviceTime = avg(self.latestLatencies) # avg latency
				# serviceTime = max(self.latestLatencies) # max latency
				
				serviceTime = np.percentile(self.latestLatencies, 95)
				self.responseTime = serviceTime
				
				#serviceTime = np.percentile(self.pastResponseTimes, 95)
				#self.responseTime = serviceTime
				
				serviceLevel = self.dimmer

				# choice of the estimator:
				# ------- bare estimator
				# self.alpha = serviceTime / serviceLevel # very rough estimate
				# ------- RLS estimation algorithm
				a = self.rlsP*serviceLevel
				g = 1 / (serviceLevel*a + self.rlsForgetting)
				k = g*a
				e = serviceTime - serviceLevel*self.alpha
				self.alpha = self.alpha + k*e
				self.rlsP  = (self.rlsP - g * a*a) / self.rlsForgetting
				# end of the estimator - in the end self.alpha should be set
				
				error = self.setpoint - serviceTime
				# NOTE: control knob allowing slow increase
				#if error > 0:
				#	error *= 0.1
				variation = (1 / self.alpha) * (1 - self.pole) * error
				serviceLevel += self.controlPeriod * variation

				# saturation, it's a probability
				self.dimmer = min(max(serviceLevel, 0.0), 1.0)
				output_dimmer = self.dimmer
		
		if len(self.latestLongLatencies) == 0:
			self.latestLongLatencies.append(0.0)
			
		if len(self.latestShortLatencies) == 0:
			self.latestShortLatencies.append(0.0)
		
		if len(self.latestLatencies) == 0:
			self.latestLatencies.append(0.0)
			
		dimmers = []
		
		for dt in self.dimmerTuples:
			dim = dt[1]
			dimmers.append(dim)
		
		# Report
		valuesToOutput = [ \
			self.sim.now, \
			self.responseTime, \
			np.percentile(self.latestLatencies, 95), \
			np.percentile(self.latestLongLatencies, 95), \
			np.percentile(self.latestShortLatencies, 95), \
			self.queueLength, \
			self.avgQueues, \
			output_dimmer, \
			output_dimmer, \
			output_dimmer, \
			avg(dimmers), \
			self.expdimmers, \
			output_dimmer, \
			output_dimmer, \
			output_dimmer, \
			output_dimmer, \
		]
		self.sim.output(self, ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))

		# Re-run later
		self.latestLatencies = []
		self.latestLongLatencies = []
		self.latestShortLatencies = []

		self.sim.add(self.controlPeriod, self.runControlLoop)

	def withOptional(self, currentQueueLength):
		
		self.updateQueueMeasures(currentQueueLength)
		self.updateDimmerMeasures(self.dimmer)	
		
		return self.random.random() <= self.dimmer, self.dimmer

	#def reportData(self, responseTime, queueLenght, timeY, timeN):
	#	#save only the latencies, the rest is not needed
	#	self.latestLatencies.append(responseTime)
		
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
