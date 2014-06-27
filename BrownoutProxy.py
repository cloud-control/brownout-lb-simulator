from __future__ import division, print_function

class BrownoutProxy:
	class Request(object):
		__slots__ = ('requestId', 'replyTo', 'expectedStartTime', 'expectedResponseTime', 'generatedAt')

	def __init__(self, sim, server, setPoint = 0.5):
		self._sim = sim
		self._server = server
		self._requests = {}
		self._timeToProcess = 0
		self._lastTimeToProcessAdjustment = 0
		self._timeY = 0.075
		self.setPoint = setPoint
		self.forgettingFactor = 0.2
		self._activeRequests = 0
		self._lastReplyWithOptional = 0

	def request(self, requestId, replyTo, headers):
		request = BrownoutProxy.Request()
		request.generatedAt = self._sim.now
		request.replyTo = replyTo
		request.requestId = requestId

		self._requests[requestId] = request
		headers = dict(headers) # copy

		dt = self._sim.now - self._lastTimeToProcessAdjustment
		self._lastTimeToProcessAdjustment = self._sim.now

		self._timeToProcess -= dt
		if self._timeToProcess < 0:
			self._timeToProcess = 0

		request.expectedStartTime = self._sim.now + self._timeToProcess
		if self._timeToProcess + self._timeY < self.setPoint:
			withOptional = True
			self._timeToProcess += self._timeY
		else:
			withOptional = False
		request.expectedResponseTime = self._timeToProcess

		self._activeRequests += 1
		headers['withOptional'] = withOptional
		self._server.request(requestId, self, headers)

		# Report
		whereToReport = str(self) + '-decision'
		valuesToOutput = [ \
			self._sim.now, \
			self._timeToProcess, \
			withOptional, \
			self._activeRequests,
		]
		self._sim.output(whereToReport, ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))

	def reply(self, requestId, headers):
		self._activeRequests -= 1
		request = self._requests[requestId]
		request.replyTo.reply(requestId, headers)
		
		if headers['withOptional']:
			self._timeY = 0.9 * self._timeY + 0.1 * min(self._sim.now - self._lastReplyWithOptional, 0.1)
			self._lastReplyWithOptional = self._sim.now

		responseTime = self._sim.now - request.generatedAt

		# Report
		self._sim.report(str(self) + '-return-path',
			responseTime = responseTime,
			expectedResponseTime = request.expectedResponseTime,
			withOptional = '1' if headers['withOptional'] else '0',
			timeY = self._timeY,
		)

	def __str__(self):
		return "brownout-proxy"
