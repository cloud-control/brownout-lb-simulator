
## Represents a request sent to an entity, waiting for a reply. This class has
# little logic, its use is basically as a dictionary.
# @note If a request needs to traverse an entity, a <b>new</b> request should be
# created, pointing to the original request.
class Request(object):
	# pylint: disable=R0903

	## Variable used for giving IDs to requests for pretty-printing
	lastRequestId = 1
	## List of allowed attributes (improves performance and reduces errors)
	__slots__ = ('requestId', 'arrival', 'completion', 'onCompleted', \
		'originalRequest', 'theta', 'withOptional', 'chosenBackendIndex',
		'remainingTime', 'createdAt')
	
	## Constructor
	def __init__(self):
		## ID of this request for pretty-printing
		self.requestId = Request.lastRequestId
		Request.lastRequestId += 1
		## Callable to call when request has completed
		self.onCompleted = lambda: ()
		## Request originating this request
		self.originalRequest = None
		## Original request creation time
		self.createdAt = None


	## Pretty-printer
	def __str__(self):
		return str(self.requestId)

