import numpy as np
import random as xxx_random # prevent accidental usage

from base.utils import *

from plants.autoscaler import AbstractAutoScalerController, BackendStatus

def getName():
	return 'idexp'

def addCommandLine(parser):
	parser.add_argument('--acIdexpImpulseTime',
		type = float,
		help = 'Specify time to apply control impulse (+1 machine)',
		default = 100,
	)

def parseCommandLine(_args):
	global args
	args = _args

def newInstance(sim, name):
	return AutoScalerController(sim, name,
		args.acIdexpImpulseTime)

class AutoScalerController(AbstractAutoScalerController):
	def __init__(self, sim, name, impulseTime):
		## Simulator kernel
		self.sim = sim

		## Controller ID for pretty-printing
		self.name = name

		self.lastTheta = {} # dictionary containing all the dimmers of the replicas
		self.status = {}
		
		# have I already applied the step
		self.done = False
		self.impulseTime = impulseTime
		self.controlInterval = impulseTime

	def onCompleted(self, request):
		self.lastTheta[request.chosenBackend] = request.theta
		return 0

	def onStatus(self, status):
		self.status = status
		return 0

	def onControlPeriod(self):
		action = 0
		sum_dimmers = sum(self.lastTheta.values())
		num_dimmers = len(self.lastTheta.values())
		average_dimmer = sum_dimmers / num_dimmers
		minimum_dimmer = min(self.lastTheta.values())
		
		if self.sim.now >= self.impulseTime and not self.done:
			action = 1
			self.done = True
				
		# Report
		valuesToOutput = [
			self.sim.now, # time
			average_dimmer, # average dimmer value
			minimum_dimmer, # minimum dimmer value
			float('nan'),
			float('nan'),
			float('nan'),
			action, # the effective action depends on infrastructure availability
		]
		self.sim.output(self, ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))
			
		self.lastTheta = {}
		return action
	
	def __str__(self):
		return self.name
