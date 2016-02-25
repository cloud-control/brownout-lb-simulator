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

## Abstract base class for all auto-scaler controllers.
# Should call autoScaler.getStatus() for control input and
# autoScaler.scaleUp()/scaleDown() for control output.
class AbstractAutoScalerController():
	def __init__(self, sim, autoScaler):
		self.autoScaler = autoScaler # pragma: no cover

	## Called when a new request arrives, before sending the request to the load-balancer.
	def onRequest(self, request):
		pass # pragma: no cover

	## Called when a request completes, potentially with information
	# piggy-backed from the load-balancer.
	def onCompleted(self, request):
		pass # pragma: no cover

## Simulates an auto-scaler.
class AutoScaler:
	## Constructor.
	# @param sim Simulator to attach to
	# @param loadBalancer loadBalancer to add/remove servers to
	# @param controlInterval control interval in case periodic control is used
	# @param startupDelay time it takes for a replica to come online
	# @param controller that decides when to scale up and when to scale down
	def __init__(self, sim, loadBalancer, startupDelay = 60, controller = None):
		## Simulator to which the autoscaler is attached
		self.sim = sim
		## Load-balancer to which the autoscaler is attached
		self.loadBalancer = loadBalancer
		## list of back-end servers to which are managed by the auto-scaler
		self.backends = []
		## count number of requests seen by the autoscaler
		self.numRequests = 0
		## startup delay
		self.startupDelay = startupDelay
		## last theta piggy-backed by load-balancer
		self.lastTheta = 1
		## controller
		self.controller = controller
		## reporting interval
		self.reportInterval = 1

		# start reporting
		self.sim.add(self.reportInterval, self.runReportLoop)

	## Adds a new back-end server and initializes decision variables.
	# @param backend the server to add
	def addBackend(self, backend):
		backend.autoScaleStatus = BackendStatus.STOPPED
		self.backends.append(backend)

	## Handles a request. The autoscaler typically only forwards requests without changing them.
	# @param request the request to handle
	def request(self, request):
		newRequest = Request()
		newRequest.originalRequest = request
		newRequest.onCompleted = lambda: self.onCompleted(newRequest)
		if self.controller:
			self.controller.onRequest(newRequest)
		self.loadBalancer.request(newRequest)

	## Handles request completion.
	# Calls orginator's onCompleted() 
	def onCompleted(self, request):
		if self.controller:
			self.controller.onCompleted(request)
		self.numRequests += 1
		originalRequest = request.originalRequest
		originalRequest.withOptional = request.withOptional
		originalRequest.onCompleted()

	## Run report loop.
	# Outputs CVS-formatted statistics through the Simulator's output routine.
	def runReportLoop(self):		
		status = self.getStatus()

		valuesToOutput = [ self.sim.now,
			status[BackendStatus.STOPPED],
			status[BackendStatus.STARTING],
			status[BackendStatus.STARTED],
			status[BackendStatus.STOPPING],
		]
		self.sim.output(self, ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))
		self.sim.add(self.reportInterval, self.runReportLoop)

	## Get status of auto-scaler
	# @return a dict with the number of backends in each state.
	# E.g., { STOPPED: 3, STARTING: 1, STARTED: 2, STOPPING: 3 }
	def getStatus(self):
		numBackends = len(self.backends)
		numStopped = len([ backend for backend in self.backends
				if backend.autoScaleStatus==BackendStatus.STOPPED ])
		numStarting = len([ backend for backend in self.backends
				if backend.autoScaleStatus==BackendStatus.STARTING ])
		numStarted = len([ backend for backend in self.backends
				if backend.autoScaleStatus==BackendStatus.STARTED ])
		numStopping = len([ backend for backend in self.backends
				if backend.autoScaleStatus==BackendStatus.STOPPING ])
		assert numBackends == numStarting + numStarted + \
				numStopped + numStopping

		return {
				BackendStatus.STOPPED : numStopped,
				BackendStatus.STARTING: numStarting,
				BackendStatus.STARTED : numStarted,
				BackendStatus.STOPPING: numStopping,
			}

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
			raise RuntimeError("AutoScaler was asked to scale up, but no backends are available.")

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
			backendToStop = [ backend for backend in self.backends
				if backend.autoScaleStatus==BackendStatus.STARTED ][-1]
		except IndexError:
			# XXX: Controller told us to scale down, but there are no backend to stop..
			# We decided to fail hard here, but another option would be to ignore the command
			raise RuntimeError("AutoScaler was asked to scale down, but no backends are started.")

		def shutdownCompleted():
			self.sim.log(self, "{0} STOPPED", backendToStop)
			backendToStop.autoScaleStatus = BackendStatus.STOPPED

		self.sim.log(self, "{0} STOPPING", backendToStop)
		backendToStop.autoScaleStatus = BackendStatus.STOPPING
		self.loadBalancer.removeBackend(backendToStop, shutdownCompleted)

	## Pretty-print auto-scaler's name.
	def __str__(self):
		return "as"

