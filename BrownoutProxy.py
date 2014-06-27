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
		self._timeY = 0.07
		self._timeN = 0.00067
		self.setPoint = setPoint

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
			self._timeToProcess += self._timeN
		request.expectedResponseTime = self._timeToProcess

		headers['withOptional'] = withOptional
		self._server.request(requestId, self, headers)

		# Report
		valuesToOutput = [ \
			self._sim.now, \
			self._timeToProcess, \
			withOptional, \
		]
		self._sim.output(str(self) + '-decision', ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))

	def reply(self, requestId, headers):
		request = self._requests[requestId]
		request.replyTo.reply(requestId, headers)

		if headers.get('withOptional'):
			self._timeY = max(self._sim.now - request.expectedStartTime, 0)
		else:
			self._timeN = max(self._sim.now - request.expectedStartTime, 0)

		# Report
		valuesToOutput = [ \
			self._sim.now, \
			self._sim.now - request.generatedAt, \
			request.expectedResponseTime, \
			headers['withOptional'], \
			self._timeY,
			self._timeN,
		]
		self._sim.output(str(self) + '-return-path', ','.join(["{0:.5f}".format(value) \
			for value in valuesToOutput]))

	def __str__(self):
		return "brownout-proxy"
