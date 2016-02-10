from __future__ import division

from Request import *
from utils import *

## Status of the replica, as seen by the auto-scaler
class BackendStatus:
	STOPPED=1
	STARTING=2
	STARTED=3
	## server does not receive any requests but needs to drain its request queue
	STOPPING=4

## Simulates an auto-scaler.
class AutoScaler:
	## Constructor.
	# @param sim Simulator to attach to
	# @param loadBalancer loadBalancer to add/remove servers to
	# @param controlInterval control interval in case periodic control is used
	# @param startupDelay time it takes for a replica to come online
	def __init__(self, sim, loadBalancer, controlInterval = 60, startupDelay = 60):
		## Simulator to which the autoscaler is attached
		self.sim = sim
		## Load-balancer to which the autoscaler is attached
		self.loadBalancer = loadBalancer
		## list of back-end servers to which are managed by the auto-scaler
		self.backends = []
		## control interval in case periodic control is used
		self.controlInterval = controlInterval
		## count number of requests seen by the autoscaler
		self.numRequests = 0
		## startup delay
		self.startupDelay = startupDelay

		# Launch control loop
		self.sim.add(0, self.runControlLoop)

	## Adds a new back-end server and initializes decision variables.
	# @param backend the server to add
	def addBackend(self, backend):
		backend.autoScaleStatus = BackendStatus.STOPPED
		self.backends.append(backend)

	## Handles a request. The autoscaler typically only forwards requests without changing them.
	# @param request the request to handle
	def request(self, request):
		# TODO: add event-driven control, if desired
		newRequest = Request()
		newRequest.originalRequest = request
		newRequest.onCompleted = lambda: self.onCompleted(newRequest)
		self.loadBalancer.request(newRequest)

	## Handles request completion.
	# Calls orginator's onCompleted() 
	def onCompleted(self, request):
		self.numRequests += 1
		originalRequest = request.originalRequest
		originalRequest.withOptional = request.withOptional
		originalRequest.onCompleted()

	## Run control loop.
	# Outputs CVS-formatted statistics through the Simulator's output routine.
	def runControlLoop(self):		
		# TODO: add periodic control, if desired

		numBackends = len(self.backends)
		numBackendsStarting = len([ backend for backend in self.backends
				if backend.autoScaleStatus==BackendStatus.STARTING ])
		numBackendsStarted = len([ backend for backend in self.backends
				if backend.autoScaleStatus==BackendStatus.STARTED ])
		numBackendsStopped = len([ backend for backend in self.backends
				if backend.autoScaleStatus==BackendStatus.STOPPED ])
		numBackendsStopping = len([ backend for backend in self.backends
				if backend.autoScaleStatus==BackendStatus.STOPPING ])
		assert numBackends == numBackendsStarting + numBackendsStarted + \
				numBackendsStopped + numBackendsStopping

		# Wait for previous scaling action to complete
		if numBackendsStarting == 0 and numBackendsStopping == 0:
			# XXX: Violates encapsulation of load-balancer
			if avg(self.loadBalancer.lastThetas) < 0.5 and numBackendsStopped > 0:
				self.scaleUp()
			elif avg(self.loadBalancer.lastThetas) > 0.9 and numBackendsStarted > 1:
				self.scaleDown()

		# Update values after control action was taken
		numBackends = len(self.backends)
		numBackendsStarting = len([ backend for backend in self.backends
				if backend.autoScaleStatus==BackendStatus.STARTING ])
		numBackendsStarted = len([ backend for backend in self.backends
				if backend.autoScaleStatus==BackendStatus.STARTED ])
		numBackendsStopped = len([ backend for backend in self.backends
				if backend.autoScaleStatus==BackendStatus.STOPPED ])
		numBackendsStopping = len([ backend for backend in self.backends
				if backend.autoScaleStatus==BackendStatus.STOPPING ])
		assert numBackends == numBackendsStarting + numBackendsStarted + \
				numBackendsStopped + numBackendsStopping

		valuesToOutput = [ self.sim.now,
			self.numRequests,
			numBackends,
			numBackendsStarting,
			numBackendsStarted
		]
		self.sim.output(self, ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))
		self.sim.add(self.controlInterval, self.runControlLoop)

	## Scale up by one replica.
	# Implemented in a FIFO-like manner, i.e., first backend added is first started.
	def scaleUp(self):
		# find first free replica
		try:
			backendToStart = [ backend for backend in self.backends
				if backend.autoScaleStatus==BackendStatus.STOPPED ][0]
		except IndexError:
			# XXX: Controller told us to scale up, but there are no backends available.
			# We decided to fail hard here, but another option would be to ignore the command
			raise Exception("AutoScaler was asked to scale up, but no backends are available.")

		def startupCompleted():
			backendToStart.autoScaleStatus = BackendStatus.STARTED
			self.loadBalancer.addBackend(backendToStart)
			self.sim.log(self, "{0} STARTED", backendToStart)

		self.sim.log(self, "{0} STARTING", backendToStart)
		backendToStart.autoScaleStatus = BackendStatus.STARTING
		self.sim.add(self.startupDelay, startupCompleted)

	## Scale down by one replica.
	# Implemented in a LIFO-like manner, i.e., last backend started is first stopped.
	def scaleDown(self):
		# Find a suitable backend to stop.
		try:
			# TODO: What is a replica is STARTING?
			backendToStop = [ backend for backend in self.backends
				if backend.autoScaleStatus==BackendStatus.STARTED ][-1]
		except IndexError:
			# XXX: Controller told us to scale down, but there are no backend to stop..
			# We decided to fail hard here, but another option would be to ignore the command
			raise Exception("AutoScaler was asked to scale down, but no backends are started.")

		def shutdownCompleted():
			self.sim.log(self, "{0} STOPPED", backendToStop)
			backendToStop.autoScaleStatus = BackendStatus.STOPPED

		self.sim.log(self, "{0} STOPPING", backendToStop)
		backendToStop.autoScaleStatus = BackendStatus.STOPPING
		self.loadBalancer.removeBackend(backendToStop, shutdownCompleted)

	## Pretty-print auto-scaler's name.
	def __str__(self):
		return "as"

