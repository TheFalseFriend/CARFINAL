# Inf3 - Computer Architecture 
# Coursework 1 - 'Understanding Branch Prediction'
# Thomas Cumming (Matric no:s1230426)

# 14/02/15

# Implemented simulations:   Static - always taken
#					   	  	 Static - always not taken
#						   	 Static - profile guided
#
#						     Dynamic - Two level correlating predictor with history k (possibly buggy)
#
#
#
# Unimplemented simulations: None




from itertools import product	# Used when calculating all possible histories of length k
import argparse 				# Command line argument parser

def cleanInstructionSet(rawInsts):
	"""Chops of the 'B' part at the start of each instruction and formats them all as (address,outcome) pairs for 
	further processing"""
	cleanedInsts=[]
	for inst in rawInsts:
		splitInst=tuple(inst.split(" "))
		cleanedInsts.append(splitInst[1:len(inst)])

	return cleanedInsts

def harvestUsedAdresses(trace):
	"""Return a list of all the unique addresses appearing in the trace"""
	return list(set([addr for (addr, outcome) in trace]))
	
def profileTrace(trace, usedAddresses):
	"""For each possible address counts the number of times that branch was taken and not taken"""
	counts = {}

	# Initialise each count to zero. Counts for an address are a pair with the left entry being the taken count
	# and the right entry being the not taken count.
	# This information is stored in a dictionary; we supply an address as a key to observe the counts for that address
	for addr in usedAddresses:
		counts.update({addr : (0,0)})
	
	for (addr,outcome) in trace:
		# For each instruction in the trace, update the tallies
		(curTCount, currNTCount)=counts[addr]
		if outcome == '1':
			counts[addr]=(curTCount+1, currNTCount)
		elif outcome == '0':
			counts[addr]=(curTCount, currNTCount+1)
		else:
			print "ERROR: Instruction set is corrupted"
	return counts

def buildPredictionMap(scheme, trace):
	"""Builds a map of our guesses for each instruction address that appears in the trace"""

	# Get a list of all the unique addresses used in the trace
	usedAddresses = harvestUsedAdresses(trace)

	# Map is represented by a dictionary
	predicitonMap = {}

	if scheme == 3:
		# 3 is profile guided

		# For each address, count the numeber of times that branch was taken and not taken
		counts = profileTrace(trace, usedAddresses)

		for addr in usedAddresses:
			# For each possible address, if the taken percentage is more than or equal to 50% make a 
			# taken prediction, otherwies a not taken one.
			totalAddrOccurrences = counts[addr][0]+counts[addr][1]
			totalTakenOutcomesForAddr = counts[addr][0]

			takenPerc = float(totalTakenOutcomesForAddr) / float(totalAddrOccurrences)
		
			# 1 is taken, 0 is not taken
			if takenPerc >= 0.5:
				predicitonMap.update({addr : 1})
			else:
				predicitonMap.update({addr : 0})

	elif scheme == 1:
		# 1 is always taken. Pred map is easy, every address just gets a taken prediction
		for addr in usedAddresses:
			predicitonMap.update({addr : 1})
	elif scheme == 2:
		# 2 is always not taken. Pred map is easy, every address just gets a not taken prediction
		for addr in usedAddresses:
			predicitonMap.update({addr : 0})

	return predicitonMap

def calculateMispredictionRate(trace, predicitonMap):
	"""For static prediction, takes in a map of our predictions for each address, and 
	calculates the misprediction rate"""
	mispredictions = 0
	totalInstCount = len(trace)

	# For each instruction in the trace, if the prediction in the map for that instruction's 
	# address doesn't match the actual outcome, we've guessed wrong, so add one to the misprediction
	# count
	for (addr,actualOutcome) in trace:
		if not(int(predicitonMap[addr]) == int(actualOutcome)):
			mispredictions=mispredictions + 1

	# Return the rate
	return float(mispredictions) / float(totalInstCount)


# Class representing a pattern history table
class PatternHistoryTable:
	def __init__(self, histLen):
		"""Initialise table entries to 01 for each row, as per the coursework handout"""

		# Determine all possible histories
		self._possibleHists = ["".join(seq) for seq in product("01", repeat=histLen)]

		# Table is represented by a dictionary
		self._table = {}

		# Populate table with default values
		for hist in self._possibleHists:
			self._table.update({hist : 1})

	def updatePredValue(self, hist, direction):
		"""Given a history to index into the table with, and instructions to decrease or increase the entry, carry 
		out the desired entry change"""

		# If we want to increase, add one unless we're already at the highest level - in which case do nothing
		assert direction in ['increase', 'decrease']
		if direction == 'increase':
			if self._table[hist] == 3:
				return
			else:
				self._table[hist] = self._table[hist] + 1		
		else:
			# If we want to decrease, subtract one unless we're already at the lowest level - in which case do nothing
			if self._table[hist] == 0:
				return
			else:
				self._table[hist]=self._table[hist] - 1
		
	def consultPHT(self, hist):
		"""Given an index, return the table entry it refers to"""
		return self._table[hist]		


class ShiftReg:
	"""Class representing a shift register. Used to model the global history register."""
	def __init__(self, len):
		"""Initialise the reg contents to be all zero as per the coursework handout"""
		self._reg = []
		self._reg = [0 for x in range(len)]
	
	def getRegContents(self):
		"""Returns a string representation of the register contents"""
		representation = ""
		for x in self._reg:
			representation = representation + str(x)
		return representation

	def updateGHR(self, valToShiftIn):
		"""Shifts the contents left by one, and shifts in valToShiftIn"""
		for i,val in enumerate(self._reg):
			if i == len(self._reg) - 1:
				self._reg[i] = valToShiftIn
			else:
				self._reg[i] = self._reg[i + 1]


# Simulator entry point
def sim(trace, args):

		if args.type == 's':
			# If we're here the user wants to simulate static branch prediciton

			# Prompt user for valid input, make them try again if they enter something unacceptable like a letter
			print "\nPlease choose the static branch prediction scheme you would like the simulator to run with."
			inputChoiceInvalid = True
			while inputChoiceInvalid:
				inputChoiceInvalid = False
				scheme = raw_input("Choices:\n1 - always taken\n2 - always not taken\n3 - profile guided\n\n>>> ")
				if not(scheme.isdigit()) or not(int(scheme) in [1,2,3]):
				 	inputChoiceInvalid = True
				 	print "ERROR: Please enter either 1, 2 or 3. Try again."

			# For pretty output
			choiceInputToStrMap = {1 : 'always taken', 2 : 'always not taken' , 3 : 'profile guided'}
			print "Using static prediction with the \'" + str(choiceInputToStrMap[int(scheme)]) + "\' policy, the simulation yields the following results:"

			# Build a map, represented as a dictionary, to store the prediction we make for each address
			predicitonMap = buildPredictionMap(int(scheme), trace) 

			simResult = calculateMispredictionRate(trace, predicitonMap)	
			print "trace misprediction rate -> %.2f%%" % (simResult * 100.0) #Output result
	

		elif args.type == 'd':
			# If we're here the user wants to run the simulation with dynamic branch prediction

			# Prompt the user to enter their choice of history length. They must choose either 4,8,12,16 and if they don't
			# we repeatedly make them try again until they enter something valid
			print "\nPlease choose the number of bits to use for storing the global history length."
			inputChoiceInvalid = True
			while inputChoiceInvalid:
				inputChoiceInvalid = False
				histLen = raw_input("Choices:\n4\n8\n12\n16\n\n>>> ")
				if not(histLen.isdigit()) or not(int(histLen) in [4,8,12,16]):
		 			inputChoiceInvalid = True
		 			print "ERROR: Please enter either 4, 8, 12 or 16. Try again."

		 	# Output for when sim is over
		 	print "Using dynamic prediction with a history length of " + str(histLen) + " bits, the simulation yields the following results:"

		 	# Create the global history register 
			GHR = ShiftReg(int(histLen))

			# Create the pattern history table
			PHT = PatternHistoryTable(int(histLen))
				
			mispredictions = 0
			totalInstCount = len(trace)
				
			# For each instruction in a trace...
			for (addr,actualOutcome) in trace:

				# Index into the PHT with the current history stored in the GHR.
				# If we have strongly taken or weakly taken, make a taken prediction for 
				# the current instruction, otherwise make a not taken prediction
				prediction = 0
				if PHT.consultPHT(GHR.getRegContents()) >= 2:
					prediction = 1
				elif PHT.consultPHT(GHR.getRegContents()) < 2:
					prediction = 0
				else:
					print "ERROR: PHT corrupted"
				
				# If what we predicted was correct, increase the 2-bit predictor for 
				# the relevant history value by one, otherwise decrease it, and icnrease the
				# misprediction count by 1 since we were wrong
				if int(prediction) == int(actualOutcome):
					PHT.updatePredValue(GHR.getRegContents(), 'increase')
				else:
					mispredictions=mispredictions + 1
					PHT.updatePredValue(GHR.getRegContents(), 'decrease')
					# Update the GHR with the actual outcome of the branch we just resolved
				GHR.updateGHR(int(actualOutcome))
				
			# Calculate the misprediction rate
			simResult = float(mispredictions) / float(totalInstCount)

			print "trace misprediction rate -> %.2f%%" % (simResult * 100.0)

# Program entry point
if __name__ == '__main__':
	
	# Set up argument parser for accepting command line args
	inArgParser = argparse.ArgumentParser(description = "A simulator to aid in the analysis of different instruction branch prediciton schemes")
	inArgParser.add_argument('type', help = 'choose to simulate static or dynamic branch prediction', choices = ['s','d'])
	inArgParser.add_argument("traceInputLoc", type = argparse.FileType('r'), help = "the location of the input trace file")
	args = inArgParser.parse_args()

	# Read in the contents of the trace files in to lists (of strings of the instructions), getting rid of newline chars. 
	rawTraceInsts = [inst.strip('\n') for inst in args.traceInputLoc.readlines()]
	
	# We're done reading files, so close them
	args.traceInputLoc.close()
	

	# Get rid of the 'B' at start of all instructions, and format each of them into a tuple (address, outcome)  and store 
	# in a list for further processing 
	cleanedInstTrace = cleanInstructionSet(rawTraceInsts)

	print "\nBranch prediction simulator - Computer Architecture"
	print "Thomas Cumming (Matric No: s1230426)"

	# Initiate the simulation
	sim(cleanedInstTrace, args)