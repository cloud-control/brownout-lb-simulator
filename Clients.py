import random as xxx_random # prevent accidental usage

## Simulates an open-loop client.
# The clients have an exponential arrival time.
class Client:
	## Constructor.
	# @param sim Simulator to attach client to
	# @param server server-like entity to which requests are sent
	# @param rate average arrival rate
	def __init__(self, sim, server, rate = 0, seed = 1):
		## average arrival rate (model parameter)
		self._rate = rate

		## simulator to which the client is attached
		self._sim = sim
		## server to which requests are issued
		self.server = server
		## separate random number generator
		self._random = xxx_random.Random()
		self._random.seed(seed)

		## Variable that measure the number of requests completed for this user
		# (metric)
		self.numCompletedRequests = 0
		## Variable that measure the number of requests completed for this user
		# with optional content (metric)
		self.numCompletedRequestsWithOptional = 0
		## Store all response times (metric)
		self.responseTimes = []

		self._scheduleRequest()
		
		# Initialize reporting
		self._sim.output(self, ','.join(['generatedAt', 'sentAt', 'repliedAt', 'responseTime', 'withOptional1', 'withOptional2']))

	## Issues a new request to the server.
	def _issueRequest(self):
		if self._rate <= 0:
			return

		# XXX: Maybe create a new event?
		self.server.request(requestId = self._sim.now,
			headers = {}, replyTo = self)

		# Schedule the next one
		self._scheduleRequest()

	## Schedules the next request.
	def _scheduleRequest(self):
		# If rate is changed from nonzero to zero, event will still be in simulator
		if self._rate > 0:
			interval = self._random.expovariate(self._rate)
			self._sim.update(interval, self._issueRequest)

	## Called when a request completes
	# @param requestId Identify the request that has completed (unused)
	# @param headers Dictionary of additional information
	def reply(self, requestId, headers):
		generatedAt = requestId # we chose to store it here
		sentAt = requestId # to maintain compatibility with httpmon dump format
		repliedAt = self._sim.now
		responseTime = repliedAt - generatedAt
		withOptional = headers.get('withOptional')
		withOptional2 = headers.get('withOptional2')

		self.numCompletedRequests += 1
		if withOptional:
			self.numCompletedRequestsWithOptional += 1
		self.responseTimes.append(responseTime)

		# Report
		valuesToOutput = [
			generatedAt,
			sentAt,
			repliedAt,
			responseTime,
			1 if withOptional else 0,
			1 if withOptional2 else 0
		]
		self._sim.output(self, ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))
		
	def setRate(self, rate):
		self._rate = rate
		self._scheduleRequest()

	## Pretty-print client's name
	def __str__(self):
		return "client"

