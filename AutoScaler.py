from __future__ import division

from Request import *
from utils import *

## Simulates an auto-scaler.
class AutoScaler:
	## Constructor.
	# @param sim Simulator to attach to
	# @param loadBalancer loadBalancer to add/remove servers to
	# @param controlInterval control interval in case periodic control is used
	def __init__(self, sim, loadBalancer, controlInterval = 60):
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

		# Launch control loop
		self.sim.add(0, self.runControlLoop)

	## Adds a new back-end server and initializes decision variables.
	# @param backend the server to add
	def addBackend(self, backend):
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
		valuesToOutput = [ self.sim.now, self.numRequests ]
		self.sim.output(self, ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))
		self.sim.add(self.controlInterval, self.runControlLoop)

	## Pretty-print auto-scaler's name.
	def __str__(self):
		return "as"

