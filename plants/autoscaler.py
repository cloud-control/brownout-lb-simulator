from __future__ import division

from base import Request

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
	def __init__(self, controlInterval):
		self.controlInterval = controlInterval

	## Called when a new request arrives, before sending the request to the load-balancer.
	# @param now simulator time when request was sent
	# @param request request that arrived at the load-balancer
	# @return 1 for scale up, 0 for do nothing, -1 for scale down
	def onRequest(self, now, request):
		return 0

	## Called when a request completes, potentially with information
	# piggy-backed from the load-balancer.
	# @param now simulator time when request was sent
	# @param request request that arrived at the load-balancer
	# @return 1 for scale up, 0 for do nothing, -1 for scale down
	def onCompleted(self, now, request):
		return 0

	## Called when the status of the autoscaler changed
	# @param now simulator time when request was sent
	# @param status new status representing number of backends in different states,
	#   e.g., { STOPPED: 1, STARTING: 1, STARTED: 2, STOPPING: 0 }
	# @return 1 for scale up, 0 for do nothing, -1 for scale down
	def onStatus(self, now, status):
		return 0

	## Called periodically, as requested by controller
	# @param now simulator time when request was sent
	# @return 1 for scale up, 0 for do nothing, -1 for scale down
	def onControlPeriod(self, now):
		return 0

## Simulates an auto-scaler.
class AutoScaler:
	## Constructor.
	# @param sim Simulator to attach to
	# @param loadBalancer loadBalancer to add/remove servers to
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
		if controller is not None:
			self.controller = controller
		else:
			self.controller = AbstractAutoScalerController(controlInterval = 1)
		## reporting interval
		self.reportInterval = 1

		# start reporting
		self.sim.add(self.reportInterval, self.runReportLoop)

		# start control
		self.sim.add(self.controller.controlInterval, self.runControlLoop)

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
		self.loadBalancer.request(newRequest)

		action = self.controller.onRequest(self.sim.now, newRequest)
		self.actuate(action)

	## Handles request completion.
	# Calls orginator's onCompleted() 
	def onCompleted(self, request):
		self.numRequests += 1
		originalRequest = request.originalRequest
		originalRequest.withOptional = request.withOptional
		originalRequest.onCompleted()

		action = self.controller.onCompleted(self.sim.now, request)
		self.actuate(action)

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

	## Run control loop.
	def runControlLoop(self):		
		action = self.controller.onControlPeriod(self.sim.now)
		self.actuate(action)
		self.sim.add(self.controller.controlInterval, self.runControlLoop)

	## Act on the control signal of the controller
	# @param action 1 for scale up, 0 for do nothing, -1 for scale down
	def actuate(self, action):
		if action == 0:
			return # no action
		elif action == 1:
			self.scaleUp()
		elif action == -1:
			self.scaleDown()
		else:
			raise RuntimeError('Invalid control action ' + str(action))

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

			action = self.controller.onStatus(self.sim.now, self.getStatus())
			self.actuate(action)

		self.sim.log(self, "{0} STARTING", backendToStart)
		backendToStart.autoScaleStatus = BackendStatus.STARTING
		self.sim.add(self.startupDelay, startupCompleted)

		action = self.controller.onStatus(self.sim.now, self.getStatus())
		self.actuate(action)

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

			action = self.controller.onStatus(self.sim.now, self.getStatus())
			self.actuate(action)

		self.sim.log(self, "{0} STOPPING", backendToStop)
		backendToStop.autoScaleStatus = BackendStatus.STOPPING
		self.loadBalancer.removeBackend(backendToStop, shutdownCompleted)
		
		action = self.controller.onStatus(self.sim.now, self.getStatus())
		self.actuate(action)

	## Pretty-print auto-scaler's name.
	def __str__(self):
		return "as"

