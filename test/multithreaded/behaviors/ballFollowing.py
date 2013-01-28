import sys
sys.path.append("..")
import utilites
import time
from pilot import *

class TurnToball(Behavior):
	def __init__(self, behaviorSelector):
		self.behaviorSelector = behaviorSelector
		self.logger = behaviorSelector.logger
		self.timeout = 10 # seconds
		self.maxAngleError = 10 # degrees

	def init(bm):
		self.startTime = time.time()
		self.ball = bm.getTarget()

	def execute(self, previousBehavior):
		output = PilotCommands()
		bm = self.behaviorSelector.ballManager
		if (previousBehavior != self):
			self.init(bm)

		if self.ball == None:
			return
		
		if time.time() - self.startTime > self.timeout:
			bm.forget(self.ball)

		desiredAngleDelta = utilities.angleCenterZero(ball.angle - self.behaviorSelector.lastArduinoInput.heading)
		output.desiredDeltaAngle = desiredDeltaAngle

		output.rollerCommand = RollerCommands.FORWARD
		output.winchCommand = WinchCommands.DOWN
		output.rampCommand = RampCommands.UP

		return output

class ApproachBall(Behavior):
	def __init__(self, behaviorSelector):
		self.behaviorSelector = behaviorSelector
		self.logger = behaviorSelector.logger
		self.forwardSpeed = 80
		self.timeout = 15 # seconds

	def init(self, ballCount):
		self.lastRunTime = None
		self.startTime = time.time()
		self.ballcount = ballCount

	def execute(self, previousBehavior):
		output = PilotCommands()
		ai = self.behaviorSelector.lastArduinoInput
		vi = self.behaviorSelector.lastVisionInput
		bs = self.behaviorSelector.behaviorStack
		bm = self.behaviorSelector.ballManager

		if previousBehavior != self:
			self.init(bm.ballCount)

		t = time.time()

		if t-self.startTime > self.timeout:
			return None # TODO ensure that we don't try to approach the ball again
		if bm.ballCount > self.ballCount: # w00t, g0t b411
			return None
		ball = bm.getTarget()
		if ball == None or not ball.recentlySeen():
			# lost the ball; hopefully this means that it is too close to us
			bs.append(DriveStraightAcquireBall(self.behaviorSelector, self.ballCount))
			return None

		if self.lastRunTime:
			angle = utilities.angleCenterZero(ball.angle - ai.heading)
			self.logger.debug("Approaching ball at {0} degrees, {1} cm".format(angle, ball.distance))
			output.desiredDeltaAngle = angle
			output.forwardSpeed = self.forwardSpeed
		else:
			output = None
		self.lastRunTime = t

		output.rollerCommand = RollerCommands.FORWARD
		output.winchCommand = WinchCommands.DOWN
		output.rampCommand = RampCommands.UP

		return output

	def getPriority(self):
		raise NotImplementedError()

class DriveStraightAcquireBall(Behavior):
	def __init__(self, behaviorManager, ballCount):
		self.behaviorManager = behaviorManager
		self.forwardSpeed = 127
		self.ballCount = ballCount
		self.timeout = 3 # seconds

	def init(self):
		self.startTime = time.time()

	def execute(self):
		output = PilotCommands()
		ai = self.behaviorSelector.lastArduinoInput
		vi = self.behaviorSelector.lastVisionInput
		bs = self.behaviorSelector.behaviorStack
		bm = self.behaviorSelector.ballManager

		pilotCommands.forwardSpeed = self.forwardSpeed

		if bm.ballCount > self.ballCount or time.time()-self.startTime > self.timeout:
			return None

		bs.append(self)

		output.rollerCommand = RollerCommands.FORWARD
		output.winchCommand = WinchCommands.DOWN
		output.rampCommand = RampCommands.UP

		return output


