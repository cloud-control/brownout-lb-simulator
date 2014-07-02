from __future__ import division, print_function

import numpy as np

class PercentileFilter:
	def __init__(self, initialValue, percentile = 90):
		self.length = 30
		self.values = [ initialValue ] * self.length
		self.index = 0
		self.percentile = percentile

	def __call__(self):
		return np.percentile(self.values, self.percentile)

	def __iadd__(self, newValue):
		self.values[self.index] = newValue
		self.index = (self.index + 1) % self.length
		return self

class BrownoutProxy:
	class Request(object):
		__slots__ = ('requestId', 'replyTo', 'generatedAt')

	def __init__(self, sim, server, setPoint = 0.5, queueCut = True, processorSharing = True):
		self._sim = sim
		self._server = server
		self._requests = {}
		self._timeToProcess = 0
		self._lastTimeToProcessAdjustment = 0
		self._timeY = PercentileFilter(0.073)
		self._timeN = PercentileFilter(0.001)
		self.setPoint = setPoint
		self.forgettingFactor = 0.2
		self._activeRequests = 0
		self._lastReply = 0
		self.queueCut = queueCut # otherwise cut based on time to process
		self.processorSharing = processorSharing

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

		if self.queueCut:
			withOptional = (self._activeRequests < (self.setPoint / self._timeY()))
		else:
			if self.processorSharing:
				withOptional = self._activeRequests * self._timeY() < self.setPoint
			else:
				withOptional = self._timeToProcess + self._timeY() < self.setPoint

		if withOptional:
			self._timeToProcess += self._timeY()
		else:
			self._timeToProcess += self._timeN()

		self._activeRequests += 1
		headers['withOptional'] = withOptional
		self._server.request(requestId, self, headers)

		# Report
		self._sim.report(str(self) + '-forward-path',
			( 'timeToProcess', 'withOptional', 'activeRequests' ),
			( self._timeToProcess, '1' if headers['withOptional'] else '0', self._activeRequests),
		)

	def reply(self, requestId, headers):
		request = self._requests[requestId]
		request.replyTo.reply(requestId, headers)
		
		responseTime = self._sim.now - request.generatedAt
		if self.processorSharing:
			serviceTime = responseTime / self._activeRequests
		else:
			serviceTime = min(self._sim.now - self._lastReply, responseTime)

		if headers['withOptional']:
			newTimeY = serviceTime
			newTimeN = float('NaN')
			self._timeY += newTimeY
		else:
			newTimeY = float('NaN')
			newTimeN = serviceTime
			self._timeN += newTimeN
		self._lastReply = self._sim.now

		self._activeRequests -= 1

		# Report
		self._sim.report(str(self) + '-return-path',
			( 'responseTime', 'withOptional', 'newTimeY', 'newTimeN', 'timeY', 'timeN'),
			( responseTime, '1' if headers['withOptional'] else '0',
			newTimeY, newTimeN, self._timeY(), self._timeN()),
		)

	def __str__(self):
		return "brownout-proxy"
