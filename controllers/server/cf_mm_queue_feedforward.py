import numpy as np
import random as xxx_random # prevent accidental usage

from base.utils import *

def getName():
	return 'mm_queue_feedforward'

def addCommandLine(parser):
	parser.add_argument('--rcMmQueueFeedforwardInitialDimmer',
		type = float,
		help = 'Specify the initial dimmer for the MM queue based controller',
		default = 0.5,
	)
	parser.add_argument('--rcMmQueueFeedforwardPeriod',
		type = float,
		help = 'Specify the control period for the MM queue based controller',
		default = 0.5,
	)
	parser.add_argument('--rcMmQueueFeedforwardDiscountFactor',
		type = float,
		help = 'Specify the discount factor for the MM queue based controller',
		default = 0.9,
	)

def parseCommandLine(_args):
	global args
	args = _args

def newInstance(sim, name):
	return MMQueueFeedforwardReplicaController(sim, name, \
		args.rcMmQueueFeedforwardInitialDimmer, args.rcPercentile, \
		args.rcMmQueueFeedforwardPeriod, args.rcSetpoint, \
		args.rcMmQueueFeedforwardDiscountFactor)

class MMQueueFeedforwardReplicaController:
	def __init__(self, sim, name, initialDimmer, percentile, period, \
		setpoint, discountFactor, seed = 1):
		## control period (controller parameter)
		self.controlPeriod = period # second
		## setpoint (controller parameter)
		self.setpoint = setpoint
		## percentile to control (controller parameter)
		self.percentile = percentile
		## latencies measured during last control period (controller input)
		self.latestLatencies = []
		## dimmer value (controller output)
		self.dimmer = initialDimmer
		## discount factor
		self.discountFactor = discountFactor
		## time to serve optional
		self.timeY = 1.0
		## time to serve mandatory
		self.timeN = 0.1
		## queue lenght
		self.queueLenght = 0

		## Reference to simulator
		self.sim = sim
		if self.controlPeriod > 0:
			self.sim.add(0, self.runControlLoop)
		
		## Random number generator
		self.random = xxx_random.Random()
		self.random.seed(seed)

		## Controller ID for pretty-printing
		self.name = name

	## Runs the control loop.
	# Basically retrieves self.lastestLatencies and computes a new self.dimmer.
	# Ask Martina for details. :P
	def runControlLoop(self):
	
		output_dimmer = float('nan')
	
		if self.latestLatencies:
			# Possible choices: max or avg latency control
			serviceTime = np.percentile(self.latestLatencies, self.percentile)
			serviceLevel = self.dimmer

			error = self.setpoint - serviceTime
			firstFactor = self.dimmer
			secondFactor = ((2 * self.setpoint / (self.timeY * (1 + self.queueLenght))) 
			  - self.timeN / self.timeY)
			serviceLevel = (1-self.discountFactor) * firstFactor + self.discountFactor * secondFactor

			# saturation, it's a probability
			self.dimmer = min(max(serviceLevel, 0.0), 1.0)
			
			output_dimmer = self.dimmer # replica is active, save correct value
		
		# Report
		valuesToOutput = [ \
			self.sim.now, \
			avg(self.latestLatencies), \
			maxOrNan(self.latestLatencies), \
			self.dimmer, \
			output_dimmer, \
		]
		self.sim.output(self, ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))

		# Re-run later
		self.latestLatencies = []
		self.sim.add(self.controlPeriod, self.runControlLoop)

	def withOptional(self):
		return self.random.random() <= self.dimmer, self.dimmer

	def reportData(self, responseTime, queueLenght, timeY, timeN):
	  # save all
		self.latestLatencies.append(responseTime)
		self.queueLenght = queueLenght
		self.timeY = timeY
		self.timeN = timeN
	
	def __str__(self):
		return self.name
