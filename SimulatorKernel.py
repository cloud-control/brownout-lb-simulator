from __future__ import print_function

from collections import deque
from heapq import heappush, heappop, heapify
import os
import sys

## Simulation kernel.
# Implements an event-driven simulator
class SimulatorKernel:
	## Constructor
	def __init__(self, outputDirectory = '.'):
		## events indexed by time
		self.events = []
		## current simulation time
		self.now = 0.0
		## cache of open file descriptors: for each issuer, this dictionary maps
		# to a file descriptor
		self.outputFiles = {}
		## output directory
		self.outputDirectory = outputDirectory

	## Adds a new event
	# @param delay non-negative float representing in how much time should the
	# event be triggered. Can be zero, in which case the simulator will trigger
	# the event a bit later, at the current simulation time.
	# @param what Event handler, can be a function, class method or lambda
	# @see Callable
	def add(self, delay, what):
		heappush(self.events, (self.now + delay, what))

	## Run the simulation
	# @param until time limit to stop simulation
	def run(self, until = 2000):
		numEvents = 0
		while self.events:
			prevNow = self.now
			self.now, event = heappop(self.events)
			#if int(prevNow / 100) < int(self.now / 100):
			#	self.log(self, "progressing, handled {0} events", numEvents)

			if self.now > until:
				return
			event()
			numEvents += 1
		self.log(self, "Handled {0} events", numEvents)

	## Log a simulation message.
	# This function is designed to simplify logging inside the simulator. It
	# prints to standard error
	# the current simulation time, the stringified issuer of the message and the
	# message itself. Includes formatting similar to String.format or
	# Logging.info.
	# @param issuer something that can be rendered as a string through str()
	# @param message the message, first input to String.format
	# @param *args,**kwargs additional arguments to pass to String.format
	def log(self, issuer, message, *args, **kwargs):
		print("{0:.6f}".format(self.now), str(issuer), \
			message.format(*args, **kwargs), file = sys.stderr)

	## Report simulation data as CSV
	# This function is designed to simplify outputting metrics from a simulated
	# entity. It prints the given line to a file, whose name is derived based on
	# the issuer (currently "sim-{issuer}.csv").
	# @param issuer something that can be rendered as a string through str()
	# @param kwargs metrics to output
	# @note current simulation time is prepended
	# is added.
	def report(self, issuer, header, values):
		outputFile = self.outputFiles.get(issuer)
		if outputFile is None:
			outputFilename = 'sim-' + str(issuer) + '.csv'
			outputFilename = os.path.join(self.outputDirectory, outputFilename)
			outputFile = open(outputFilename, 'w')
			print('now', *header, sep = ',', file = outputFile)
			self.outputFiles[issuer] = outputFile

		print(self.now, *values, sep = ',', file = outputFile)

	## Pretty-print the simulator kernel's name
	def __str__(self):
		return "kernel"
