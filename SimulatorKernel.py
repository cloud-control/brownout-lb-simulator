from __future__ import print_function

from collections import defaultdict, deque
import os
import sys

## Simulation kernel.
# Implements an event-driven simulator
class SimulatorKernel:
	## Constructor
	def __init__(self, outputDirectory = '.'):
		## events indexed by time
		self.events = defaultdict(list)
		## reverse index from event handlers to time index, to allow easy update
		self.whatToTime = {}
		## current simulation time
		self.now = 0.0
		## cache of open file descriptors: for each issuer, this dictionary maps
		# to a file descriptor
		self.outputFiles = {}
		## output directory
		self.outputDirectory = outputDirectory
		self.optionalOn = 0
		self.optionalOff = 0
		self.avgServiceTime = 0
		self.stdServiceTime = 0

	## Adds a new event
	# @param delay non-negative float representing in how much time should the
	# event be triggered. Can be zero, in which case the simulator will trigger
	# the event a bit later, at the current simulation time.
	# @param what Event handler, can be a function, class method or lambda
	# @see Callable
	def add(self, delay, what):
		self.events[self.now + delay].append(what)
		self.whatToTime[what] = self.now + delay

	## Update an existing event or add a new event
	# @param delay in how much time should the event be triggered
	# @param what Callable to call for handling this event. Can be a function,
	# class method or lambda
	# @note Deletes the previously existing event that is handled by what.
	# The current implementation stores at most one such event.
	def update(self, delay, what):
		if what in self.whatToTime:
			oldTime = self.whatToTime[what]
			events = self.events[oldTime]
			events.remove(what)
			if len(events) == 0:
				del self.events[oldTime]
			del self.whatToTime[what]
		self.add(delay, what)

	## Run the simulation
	# @param until time limit to stop simulation
	def run(self, until = 2000):
		numEvents = 0
		while self.events:
			prevNow = self.now
			self.now = min(self.events)
			#if int(prevNow / 100) < int(self.now / 100):
			#	self.log(self, "progressing, handled {0} events", numEvents)
			events = self.events[self.now]
			event = events.pop()
			del self.whatToTime[event]
			if len(events) == 0:
				del self.events[self.now]

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

	## Output simulation data.
	# This function is designed to simplify outputting metrics from a simulated
	# entity. It prints the given line to a file, whose name is derived based on
	# the issuer (currently "sim-{issuer}.csv").
	# @param issuer something that can be rendered as a string through str()
	# @param outputLine the line to output
	# @note outputLine is written verbatimly to the output file, plus a newline
	# is added.
	def output(self, issuer, outputLine):
		if issuer not in self.outputFiles:
			outputFilename = 'sim-' + str(issuer) + '.csv'
			outputFilename = os.path.join(self.outputDirectory, outputFilename)
			self.outputFiles[issuer] = open(outputFilename, 'w')
		outputFile = self.outputFiles[issuer]
		outputFile.write(outputLine + "\n")

		# kills performance, but reduces experimenter's impatience :D
		outputFile.flush()

	## Pretty-print the simulator kernel's name
	def __str__(self):
		return "kernel"
