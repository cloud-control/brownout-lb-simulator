import random

from Request import *

## Simulates an open-loop client.
# The clients have an exponential arrival time.
class OpenLoopClient:
	## Constructor.
	# @param sim Simulator to attach client to
	# @param server server-like entity to which requests are sent
	# @param rate average arrival rate
	def __init__(self, sim, server, rate = 0):
		## average arrival rate (model parameter)
		self.rate = rate

		## simulator to which the client is attached
		self.sim = sim
		## server to which requests are issued
		self.server = server

		## Variable that measure the number of requests completed for this user
		# (metric)
		self.numCompletedRequests = 0
		## Variable that measure the number of requests completed for this user
		# with optional content (metric)
		self.numCompletedRequestsWithOptional = 0
		## Store all response times (metric)
		self.responseTimes = []

		self.scheduleRequest()

	## Issues a new request to the server.
	def issueRequest(self):
		if self.rate <= 0:
			return

		request = Request()
		request.createdAt = self.sim.now
		request.onCompleted = lambda: self.onCompleted(request)
		self.server.request(request)

		# Schedule the next one
		self.scheduleRequest()

	## Schedules the next request.
	def scheduleRequest(self):
		# If rate is changed from nonzero to zero, event will still be in simulator
		if self.rate > 0:
			interval = random.expovariate(self.rate)
			self.sim.update(interval, self.issueRequest)

	## Called when a request completes
	# @param request the request that has been completed
	def onCompleted(self, request):
		self.numCompletedRequests += 1
		if request.withOptional:
			self.numCompletedRequestsWithOptional += 1
		self.responseTimes.append(self.sim.now - request.createdAt)
		
	def setRate(self, rate):
		self.rate = rate
		self.scheduleRequest()

## Simulates a closed-loop client.
# The client waits for a request to complete before issuing a new one.
class ClosedLoopClient:
	## Variable used for giving IDs for pretty-printing
	lastClientId = 1

	## Constructor.
	# @param sim Simulator to attach client to
	# @param server server-like entity to which requests are sent
	# @param thinkTime average think-time between issuing consecutive requests
	def __init__(self, sim, server, thinkTime = 1):
		## average think-time (model parameter)
		self.averageThinkTime = thinkTime
		## ID of this client used for pretty-printing
		self.name = 'client' + str(ClosedLoopClient.lastClientId)
		ClosedLoopClient.lastClientId += 1

		## simulator to which the client is attached
		self.sim = sim
		## server to which requests are issued
		self.server = server

		## Variable that measure the number of requests completed for this user
		# (metric)
		self.numCompletedRequests = 0
		## Variable that measure the number of requests completed for this user
		# with optional content (metric)
		self.numCompletedRequestsWithOptional = 0
		## Store all response times (metric)
		self.responseTimes = []
		## Variable used to deactive the client
		self.active = True
		
		# Launch client in the thinking phase
		self.sim.add(0, self.think)

	## Issues a new request to the server.
	def issueRequest(self):
		if not self.active:
			return
		request = Request()
		request.createdAt = self.sim.now
		request.onCompleted = lambda: self.onCompleted(request)
		#self.sim.log(self, "Requested {0}", request)
		self.server.request(request)

	## Called when a request completes
	# @param request the request that has been completed
	def onCompleted(self, request):
		self.numCompletedRequests += 1
		if request.withOptional:
			self.numCompletedRequestsWithOptional += 1
		self.responseTimes.append(self.sim.now - request.createdAt)
		self.think()

	def think(self):
		thinkTime = random.expovariate(1.0 / self.averageThinkTime)
		self.sim.add(thinkTime, self.issueRequest)

	## Deactive this client.
	# The client will not issue any more requests and no new simulator events
	# are created. Hence, the object can be garbage-collected.
	def deactivate(self):
		self.active = False
	
	## Pretty-print client's name
	def __str__(self):
		return self.name

