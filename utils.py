from __future__ import division, print_function
import random
# for numpy >= 1.7
#from numpy.random import choice

## Randomly picks an item from several choices, as given by the attached
# weights. Sum of weight must equal 1.
# Example: @code weightedChoice([('a', 0.1), ('b', 0.9)]) @endcode
#
# @param choiceWeightPairs list of pairs to choose from; first item in pair is
# choice, second is weight
def weightedChoice(choiceWeightPairs):
	# for numpy >= 1.7
	#weights  = [w for c,w in choiceWeightPairs]
	#elements = [c for c,w in choiceWeightPairs]
	#weights  = [w/sum(weights) for w in weights]
	#return choice(elements, p=weights)
	totalWeight = sum(weight for choice, weight in choiceWeightPairs)
	rnd = random.uniform(0, totalWeight)
	upto = 0
	for choice, weight in choiceWeightPairs:
		if upto + weight > rnd:
			return choice
		upto += weight
	assert False, "Shouldn't get here"

## Computes average
# @param numbers list of number to compute average for
# @return average or NaN if list is empty
def avg(numbers):
	if len(numbers) == 0:
		return float('nan')
	return sum(numbers)/len(numbers)

## Computes maximum
# @param numbers list of number to compute maximum for
# @return maximum or NaN if list is empty
# @note Similar to built-in function max(), but returns NaN instead of throwing
# exception when list is empty
def maxOrNan(numbers):
	if len(numbers) == 0:
		return float('nan')
	return max(numbers)

## Normalize a list, so that the sum of all elements becomes 1
# @param numbers list to normalize
# @return normalized list
def normalize(numbers):
	if len(numbers) == 0:
		# Nothing to do
		return [ ]
	
	s = sum(numbers)
	if s == 0:
	# How to normalize a zero vector is a matter of much debate
		return [ float('nan') ] * len(numbers)
	return [ n / s for n in numbers ]
