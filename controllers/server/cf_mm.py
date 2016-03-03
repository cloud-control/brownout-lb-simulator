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

	## Runs the control loop.
	# Basically retrieves self.lastestLatencies and computes a new self.dimmer.
	# Ask Martina for details. :P
	def runControlLoop(self):
		if self.latestLatencies:
			# Possible choices: max or avg latency control
			#serviceTime = avg(self.latestLatencies) # avg latency
			# serviceTime = max(self.latestLatencies) # max latency
			serviceTime = np.percentile(self.latestLatencies, self.percentile)
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
		
		# Report
		valuesToOutput = [ \
			self.sim.now, \
			avg(self.latestLatencies), \
			maxOrNan(self.latestLatencies), \
			self.dimmer, \
		]
		self.sim.output(self, ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))

		# Re-run later
		self.latestLatencies = []
		self.sim.add(self.controlPeriod, self.runControlLoop)

	def withOptional(self):
		return self.random.random() <= self.dimmer, self.dimmer

	def reportData(self, responseTime, queueLenght, timeY, timeN):
	  # save only the latencies, the rest is not needed
		self.latestLatencies.append(responseTime)
	
	def __str__(self):
		return self.name
