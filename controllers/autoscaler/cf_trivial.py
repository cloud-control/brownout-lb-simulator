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

		self.lastTheta = None
		self.status = {}

	def onCompleted(self, request):
		self.lastTheta = request.theta
		return 0

	def onStatus(self, status):
		self.status = status
		return 0

	def onControlPeriod(self):
		action = 0

		if \
				self.status[BackendStatus.STOPPING] == 0 or \
				self.status[BackendStatus.STARTING] == 0:
					if self.lastTheta > self.scaleDownThreshold:
						if self.status[BackendStatus.STARTED] > 0:
							action = -1
					elif self.lastTheta < self.scaleUpThreshold:
						if self.status[BackendStatus.STOPPED] > 0:
							action = +1

		# Report
		valuesToOutput = [
			self.sim.now,
			self.lastTheta,
			action,
		]
		self.sim.output(self, ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))
		return action
	
	def __str__(self):
		return self.name
