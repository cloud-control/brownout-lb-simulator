from __future__ import division, print_function

from math import sqrt
import numpy as np

from recordtype import recordtype

# pylint: disable=too-few-public-methods
class VarianceBasedFilter(object):
	def __init__(self, sigmaWeight, initialValue):
		self.num = 0
		self.mean = initialValue
		self.variance = 0
		self.sigmaWeight = sigmaWeight

	def __call__(self):
		return self.mean + self.sigmaWeight * sqrt(self.variance)

	def __iadd__(self, newValue):
		self.num += 1
		self.mean = (self.num - 1) / self.num * self.mean + 1.0 / self.num * newValue
		if self.num > 1:
			self.variance = (
				(self.num - 1) / self.num * self.variance +
				1.0 / (self.num - 1) * (newValue - self.mean) ** 2)
		return self

# pylint: disable=no-member
class PercentileBasedFilter(object):
	def __init__(self, initialValue, windowLength=100, percentile=99):
		self._samples = np.array([initialValue] * windowLength)
		self._index = 0
		self._windowLength = windowLength
		self._percentile = percentile

	def __call__(self):
		return np.percentile(self._samples, self._percentile)

	def __iadd__(self, newValue):
		self._samples[self._index] = newValue
		self._index = (self._index + 1) % self._windowLength
		return self
# pylint: enable=too-few-public-methods,no-member

class BrownoutProxy(object):
	Request = recordtype('Request', 'generatedAt replyTo requestId time')

	def __init__(self, sim, server, setPoint=0.5, queueCut=True,
		processorSharing=True):

		self._sim = sim
		self._server = server
		self._requests = {}
		self._timeToProcess = 0
		self._lastTimeToProcessAdjustment = 0

		sigmaWeight = 0
		self._timeY = VarianceBasedFilter(initialValue=0.200, sigmaWeight=sigmaWeight)
		self._timeN = VarianceBasedFilter(initialValue=0.001, sigmaWeight=sigmaWeight)
		self.setPoint = setPoint
		self.forgettingFactor = 0.2
		self._activeRequests = 0
		self._activeRequestsWithOptional = 0
		self._activeRequestsWithoutOptional = 0
		self._lastReply = 0
		self.queueCut = queueCut # otherwise cut based on time to process
		self.processorSharing = processorSharing

	def request(self, requestId, replyTo, headers):
		request = BrownoutProxy.Request(generatedAt=self._sim.now,
			replyTo=replyTo,
			requestId=requestId,
			time=0)
		self._requests[requestId] = request
		headers = dict(headers) # copy

		self._activeRequests += 1

		withOptional = self._timeToProcess + self._timeY() < self.setPoint
		if withOptional:
			request.time = self._timeY()
		else:
			request.time = self._timeN()
		self._timeToProcess += request.time

		headers['withOptional'] = withOptional
		self._server.request(requestId, self, headers)

		# Report
		self._sim.report(str(self) + '-forward-path',
			('timeToProcess', 'withOptional', 'activeRequests'),
			(self._timeToProcess, '1' if headers['withOptional'] else '0',
			self._activeRequests),
		)

	def reply(self, requestId, headers):
		request = self._requests[requestId]
		request.replyTo.reply(requestId, headers)

		responseTime = self._sim.now - request.generatedAt
		self._timeToProcess -= request.time

		if headers['withOptional']:
			newTimeY = responseTime
			newTimeN = float('NaN')
			self._timeY += newTimeY
			self._activeRequestsWithOptional -= 1
		else:
			newTimeY = float('NaN')
			newTimeN = responseTime
			self._timeN += newTimeN
			self._activeRequestsWithoutOptional += 1
		self._lastReply = self._sim.now

		self._activeRequests -= 1

		# Report
		self._sim.report(str(self) + '-return-path',
			('responseTime', 'withOptional',
			'activeWithOptional','activeWithoutOptional',
			'newTimeY', 'newTimeN', 'timeY', 'timeN'),
			(responseTime, '1' if headers['withOptional'] else '0',
			self._activeRequestsWithOptional, self._activeRequestsWithoutOptional,
			newTimeY, newTimeN, self._timeY(), self._timeN()),
		)

	def __str__(self):
		return "brownout-proxy"
