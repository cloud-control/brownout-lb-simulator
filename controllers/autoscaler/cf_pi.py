import numpy as np
import random as xxx_random # prevent accidental usage

from base.utils import *

from plants.autoscaler import AbstractAutoScalerController, BackendStatus

def getName():
	return 'pi'

def addCommandLine(parser):
	parser.add_argument('--acPIProportionalGain',
		type = float,
		help = 'Specify the gain of the proportional controller part',
		default = 0.8,
	)
	parser.add_argument('--acPIIntegralGain',
		type = float,
		help = 'Specify the gain of the integral controller part',
		default = 0.6,
	)
	parser.add_argument('--acPIControlInterval',
		type = float,
		help = 'Specify the control interval for the PI controller',
		default = 300, # 300 --> 5 minutes, 600 --> 10 minutes
	)
	parser.add_argument('--acPISetpoint',
		type = float,
		help = 'Specify the Setpoint for the PI controller',
		default = 0.45,
	)

def parseCommandLine(_args):
	global args
	args = _args

def newInstance(sim, name):
	return AutoScalerController(sim, name,
		args.acPIProportionalGain,
		args.acPIIntegralGain,
		args.acPIControlInterval,
		args.acPISetpoint)

class AutoScalerController(AbstractAutoScalerController):
	def __init__(self, sim, name, proportionalGain, integralGain, controlInterval, setpoint):
		## Simulator kernel
		self.sim = sim

		## Controller ID for pretty-printing
		self.name = name

		## control parameters
		self.controlInterval = controlInterval # read from the autoscaler
		self.proportionalGain = proportionalGain # read from command line
		self.integralGain = integralGain # read from command line
		self.setpoint = setpoint # read from command line

		self.lastTheta = {} # dictionary containing all the dimmers of the replicas
		self.status = {}
		self.average_dimmer = 0.0 # for logging and control purposes
		self.controlValue = 0 # increment/decrement replica numbers
		
		self.proportionalPart = 0.0 # initialization for the proportional part
		self.integralPart = 0.0 # initialization for the integral part

	def onCompleted(self, request):
		self.lastTheta[request.chosenBackendIndex] = request.theta
		return 0

	def onStatus(self, status):
		self.status = status
		return 0

	def onControlPeriod(self):
		action = 0

		# do something only if the previous action has been completed
		if \
				self.status[BackendStatus.STOPPING] == 0 and \
				self.status[BackendStatus.STARTING] == 0:
					# compute the average of dimmer values (maybe we will use the min?)
					sum_dimmers = sum(self.lastTheta.values())
					num_dimmers = len(self.lastTheta.values())
					self.average_dimmer = sum_dimmers / num_dimmers
					
					# control value computation
					error = self.setpoint - self.average_dimmer
					self.proportionalPart = self.proportionalGain * error
					nonquantizedControl = self.proportionalPart + self.integralPart
					self.controlValue = round(nonquantizedControl)
					print (error, nonquantizedControl, self.controlValue)
					
					# control value application
					action = self.controlValue
					
					# update
					self.integralPart = self.integralPart + self.integralGain * error

		# Report
		valuesToOutput = [
			self.sim.now,
			self.average_dimmer,
			action,
		]
		self.sim.output(self, ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))
		return action
	
	def __str__(self):
		return self.name
