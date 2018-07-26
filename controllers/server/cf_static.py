import random as xxx_random # prevent accidental usage

def getName():
	return 'static'

def addCommandLine(parser):
	parser.add_argument('--rcStaticDimmer',
		type = float,
		help = 'Specify a dimmer for the static controller',
		default = 1.0,
	)

def parseCommandLine(args):
	global staticDimmer
	staticDimmer = args.rcStaticDimmer

def newInstance(sim, server, name):
	return StaticReplicaController(sim, name)

class StaticReplicaController:
	def __init__(self, sim, name, seed = 1):
		self.name = name
		self.sim  = sim

		## Random number generator
		self.random = xxx_random.Random()
		self.random.seed(seed)

	def __str__(self):
		return self.name

	def withOptional(self, request):
		return self.random.random() <= staticDimmer, staticDimmer

	def decidePacketRequest(self):
		pass

	def reportData(self, newArrival, responseTime, queueLength, timeY, timeN, optional, serviceTime, avgServiceTimeSetpoint):
		# Not needed for the static controller
		pass
