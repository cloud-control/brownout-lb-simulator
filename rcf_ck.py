from __future__ import division, print_function

import numpy as np

import random
from utils import *

def addCommandLine(parser):
	parser.add_argument('--rcCkPole',
		type = float,
		help = 'Specify the pole for the CK controller',
		default = 0.9,
	)
	parser.add_argument('--rcCkRlsForgetting',
		type = float,
		help = 'Specify the RLS forgetting factor for the CK controller',
		default = 0.95,
	)

def parseCommandLine(_args):
	global args
	args = _args

def newInstance(sim, name):
	return CKReplicaController(sim, name, \
		args.rcPercentile, \
		args.rcCkPole, args.rcCkRlsForgetting, \
		args.rcSetpoint)

class CKReplicaController:
	def __init__(self, sim, name, percentile, pole, \
		rlsForgetting, setpoint, seed = 1):
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
		## current queue time
		self.queueTime = 0
		self.queueLength = 0
		self.lastQueueTimeCheck = 0

		## time to serve optional
		self.timeY = 0.0070
		## time to serve mandatory
		self.timeN = 0.00067

		## Reference to simulator
		self.sim = sim
		
		## Controller ID for pretty-printing
		self.name = name

	def withOptional(self):
		# Update queue time
		self.queueTime -= self.sim.now - self.lastQueueTimeCheck
		self.lastQueueTimeCheck = self.sim.now
		if self.queueTime < 0: self.queueTime = 0

		withOptional = (self.queueLength < 400)

		if withOptional:
			self.queueTime += self.timeY
		else:
			self.queueTime += self.timeN
		self.queueLength += 1
		return withOptional, 0

	def reportData(self, responseTime, queueLenght, timeY, timeN, withOptional):
		self.queueLength -= 1
		self.timeY = timeY
		self.timeN = timeN
		self.latestLatencies.append(responseTime)
	
	def __str__(self):
		return self.name

def computeMB1(serviceRateY, serviceRateN, queueThreshold, arrivalRate):
	roM = arrivalRate / serviceRateY
	rom = arrivalRate / serviceRateN
	qhat = queueThreshold

	pi0 = 1 / ((1-roM**qhat)/(1-roM) + (roM**qhat)/(1-rom))
	A = (1 - roM**qhat) / ((1 - roM)**2) - (1 + (qhat - 1) * (roM ** qhat)) / (1 - roM)
	B = rom / ((1 - rom) ** 2) + qhat / (1 - rom)

	q = pi0 * (A + (roM ** qhat) * B)
	return q / arrivalRate

if __name__ == "__main__":
	for queueThreshold in range(0, 400):
		print(queueThreshold, computeMB1(1/0.0070, 1/0.00067, queueThreshold, 400))

