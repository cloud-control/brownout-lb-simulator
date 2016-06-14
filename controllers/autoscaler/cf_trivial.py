import numpy as np
import random as xxx_random # prevent accidental usage

from base.utils import *

from plants.autoscaler import AbstractAutoScalerController, BackendStatus

def getName():
	return 'trivial'

def addCommandLine(parser):
	parser.add_argument('--acTrivialScaleDownThreshold',
		type = float,
		help = 'Specify the dimmer above which to scale down',
		default = 1,
	)
	parser.add_argument('--acTrivialScaleUpThreshold',
		type = float,
		help = 'Specify the dimmer below which to scale up',
		default = 0,
	)
	parser.add_argument('--acTrivialControlInterval',
		type = float,
		help = 'Specify the control interval',
		default = 1,
	)

def parseCommandLine(_args):
	global args
	args = _args

def newInstance(sim, name):
	return AutoScalerController(sim, name,
		args.acTrivialScaleDownThreshold,
		args.acTrivialScaleUpThreshold,
		args.acTrivialControlInterval)

class AutoScalerController(AbstractAutoScalerController):
	def __init__(self, sim, name, scaleDownThreshold, scaleUpThreshold, controlInterval):
		self.scaleDownThreshold = scaleDownThreshold
		self.scaleUpThreshold = scaleUpThreshold

		## Simulator kernel
		self.sim = sim

		## Controller ID for pretty-printing
		self.name = name

		## control interval (read by autoscaler)
		self.controlInterval = controlInterval

		self.lastTheta = float('nan')
		self.status = {}

	def onCompleted(self, request):
		self.lastTheta = request.theta
		return 0

	def onStatus(self, status):
		self.status = status
		return 0

	def onControlPeriod(self):
		if \
				self.status[BackendStatus.STOPPING] != 0 or \
				self.status[BackendStatus.STARTING] != 0:
			return

		numStartedReplicas = self.status[BackendStatus.STARTED]
		numStoppedReplicas = self.status[BackendStatus.STOPPED]

		numReplicas = float('nan') # by default, no change
		if self.lastTheta > self.scaleDownThreshold:
			numReplicas = max(numStartedReplicas-1, 0)
		elif self.lastTheta < self.scaleUpThreshold:
			numReplicas = max(numStartedReplicas+1, 0)

		# Report
		valuesToOutput = [
			self.sim.now,
			self.lastTheta,
			numReplicas,
		]
		self.sim.output(self, ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))
		return numReplicas
	
	def __str__(self):
		return self.name
