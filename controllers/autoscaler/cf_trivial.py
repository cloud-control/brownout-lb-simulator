import numpy as np
import random as xxx_random # prevent accidental usage

from base.utils import *

from plants.autoscaler import AbstractAutoScalerController

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

def parseCommandLine(_args):
	global args
	args = _args

def newInstance(sim, name):
	return AutoScalerController(sim, name,
		args.acTrivialScaleDownThreshold,
		args.acTrivialScaleUpThreshold)

class AutoScalerController(AbstractAutoScalerController):
	def __init__(self, sim, name, scaleDownThreshold, scaleUpThreshold):
		self.scaleDownThreshold = scaleDownThreshold
		self.scaleUpThreshold = scaleUpThreshold

		## Simulator kernel
		self.sim = sim

		## Controller ID for pretty-printing
		self.name = name

		self.lastTheta = None

	def onCompleted(self, now, request):
		self.lastTheta = request.theta

	def onControlPeriod(self, now, request):
		# Report
		valuesToOutput = [ \
			self.sim.now, \
			self.lastTheta, \
		]
		self.sim.output(self, ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))
	
	def __str__(self):
		return self.name
