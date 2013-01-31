import sys
sys.path.append("..")
import utilities
from behavior import Behavior
from pilot import *
import time

class LiftBasket(Behavior):
	def __init__(self, behaviorManager):
		self.timeout = 15 # seconds

	def init(self):
		self.startTime = time.time()

	def execute(self, previousBehavior):
		if previousBehavior != self:
			self.init()

		if self.behaviorManager.lastArduinoInput.winchTop or time.time() - self.startTime > self.timeout:
			self.behaviorManager.behaviorStack.append(WaitWhileScoring(self.behaviorManager))
		else:
			self.behaviormanager.behaviorStack.append(self)

		outputs = PilotCommands()
		
		outputs.forwardSpeed = 0
		outputs.turnSpeed = 0
		outputs.rampCommand = RampCommands.DOWN
		outputs.winchCommand = WinchCommands.UP
		outputs.rollerCommand = RollerCommands.FORWARD

class WaitWhileScoring(Behavior):
	def __init__(self, behaviorManager):
		self.timeout = 10 # seconds

	def init(self):
		self.startTime = time.time()

	def execute(self, previousBehavior):
		if previousBehavior != self:
			self.init()

		if time.time() - self.startTime > self.timeout:
			self.behaviorManager.behaviorStack.append(LowerBasket(self.behaviorManager))
		else:
			self.behaviorManager.behaviorStack.append(self)

		outputs = PilotCommands()
		
		outputs.forwardSpeed = 0
		outputs.turnSpeed = 0
		outputs.rampCommand = RampCommands.DOWN
		outputs.winchCommand = WinchCommands.UP
		outputs.rollerCommand = RollerCommands.STOP

class LowerBasket(Behavior):
	def __init__(self, behaviorManager):
		self.timeout = 15 # seconds

	def init(self):
		self.startTime = time.time()

	def execute(self, previousBehavior):
		if previousBehavior != self:
			self.init()

		if self.behaviorManager.lastArduinoInput.winchBottom or time.time() - self.startTime > self.timeout:
			return
		else:
			self.behaviormanager.behaviorStack.append(self)

		outputs = PilotCommands()
		
		outputs.forwardSpeed = 0
		outputs.turnSpeed = 0
		outputs.rampCommand = RampCommands.UP
		outputs.winchCommand = WinchCommands.DOWN
		outputs.rollerCommand = RollerCommands.STOP

