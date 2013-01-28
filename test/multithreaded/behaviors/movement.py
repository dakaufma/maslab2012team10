import sys
sys.path.append("..")
import utilites
import time
from pilot import *

class DriveStraight(Behavior):
	"""Goes forward. Can change states to track a ball or avoid a wall"""

	def __init__(self, behaviorSelector):
		self.behaviorSelector = behaviorSelector
		self.logger = behaviorSelector.logger
		self.forwardSpeed = 127
		self.minDist = 25 # cm

	def execute(self, previousBehavior):
		ai = self.behaviorSelector.lastArduinoInput
		vi = self.behaviorSelector.lastVisionInput
		bs = self.behaviorSelector.behaviorStack
		bm = self.behaviorSelector.ballManager

		if utilities.crashed(ai):
			bs.append(Uncrash(self.behaviorSelector))
		elif utilities.nearWall(ai):
			bs.append(AvoidWall(self.behaviorSelector))


		output = PilotCommands()
		output.forwardSpeed = self.forwardSpeed
		output.rollerCommand = RollerCommands.FORWARD
		output.winchCommand = WinchCommands.DOWN
		output.rampCommand = RampCommands.UP

		return output

class AvoidWall(Behavior):
	def __init__(self, behaviorSelector):
		self.behaviorSelector = behaviorSelector
		self.logger = behaviorSelector.logger
		self.turnSpeed = 127
		self.forwardSpeed = 127
		self.minDist = utilities.nearWallDist
		self.logger = logger

	def execute(self, previousBehavior):
		output = PilotCommands()
		ai = self.behaviorSelector.lastArduinoInput
		vi = self.behaviorSelector.lastVisionInput
		bs = self.behaviorSelector.behaviorStack
		bm = self.behaviorSelector.ballManager

		if utilities.crashed(ai):
			bs.append(self)
			bs.append(Uncrash(self.behaviorSelector))
			return None
		elif ai.leftDist < self.minDist and ai.leftDist <= ai.rightDist:
			output.forwardSpeed = -self.forwardSpeed
			output.turnSpeed = self.turnSpeed
			self.logger.debug("Avoiding wall on the left")
			bs.append(self) # TODO implement a timeout
		elif ai.rightDist < self.minDist:
			output.forwardSpeed = -self.forwardSpeed
			output.turnSpeed = -self.turnSpeed
			self.logger.debug("Avoiding wall on the right")
			bs.append(self) # TODO implement a timeout
		
		output.rollerCommand = RollerCommands.FORWARD
		output.winchCommand = WinchCommands.DOWN
		output.rampCommand = RampCommands.UP

		return output

class Uncrash(Behavior):
	def __init__(self, behaviorSelector):
		self.behaviorSelector = behaviorSelector
		self.logger = behaviorSelector.logger
		self.forwardSpeed = 127
		self.turnSpeed = 80

	def init(ai):
		self.crashedRight = ai.frBump or ai.brBump
		self.crashedLeft = ai.flBump or ai.blBump
		self.crashedFront = ai.frBump or flBump
		self.crashedBack = ai.brBump or blBump

	def execute(self, previousBehavior):
		output = PilotCommands()
		ai = self.behaviorSelector.lastArduinoInput
		vi = self.behaviorSelector.lastVisionInput
		bs = self.behaviorSelector.behaviorStack
		bm = self.behaviorSelector.ballManager
		
		if (previousBehavior != self):
			self.init(ai)

		if utilities.crashed(ai):
			bs.append(self)

			if self.crashedFront and self.crashedBack:
				self.logger.warn("Crashed front and back. This really sucks.")
				output.turnSpeed = 127
			elif self.crashedFront:
				output.forwardSpeed = -self.forwardSpeed
				output.turnSpeed = self.turnSpeed * ((1 if self.crashedLeft else 0) - (1 if self.crashedRight else 0))
			else: # crashed back
				output.forwardSpeed = self.forwardSpeed
				output.turnSpeed = self.turnSpeed * ((1 if self.crashedLeft else 0) - (1 if self.crashedRight else 0))
		else:
			output = None
		
		output.rollerCommand = RollerCommands.FORWARD
		output.winchCommand = WinchCommands.DOWN
		output.rampCommand = RampCommands.UP

		return output

class StopPermanently(Behavior):
	def __init__(self, behaviorManager):
		self.behaviorManager = behaviorManager
		self.logger = behaviorManager.logger

	def execute(self, previousState):
		self.behaviorManager.behaviorStack.append(this)
		return PilotCommands()


class ForcedMarch(Behavior):
	"""Forces the robot to ignore balls, towers, etc for a certain time period and just drive around. Intended as a means of resetting the robot when something goes wrong."""

	def __init__(self, behaviorManager):
		self.behaviorManager = behaviorManager
		self.logger = logger
		self.forward = DriveStraight(behaviorManager)
		self.timeout = 10 # sec

	def init(self):
		self.startTime = time.time()

	def execute(self, previousState):
		if (previousState != self and previousState != self.forward):
			self.init()

		if time.time() - self.startTime < timeout: # robot is forced to march (drive straight) until the timeout is reached
			self.behaviorManager.behaviorStack.append(self)
			self.behaviorManager.behaviorStack.append(forward)
		return None

