#!/usr/bin/env python
from __future__ import division, print_function

import os
import sys

def loadControllerFactories(plantType):
	controllerFactories = []
	controllerFactoriesDir = os.path.join('controllers', plantType)
	for filename in os.listdir(controllerFactoriesDir):
		# Not a controller factory
		if filename[:3] != "cf_": continue
		if filename[-3:] != ".py": continue

		# Load Python module
		controllerFactory = __import__('controllers.' +
				plantType + '.' + os.path.splitext(filename)[0],
			fromlist = ['getName', 'addCommandLine', 'parseCommandLine', 'newInstance' ])
		controllerFactories.append(controllerFactory)
	return controllerFactories

