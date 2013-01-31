from pilot import *
from behavior import Behavior
import utilities

class TurnToBall(Behavior):
	def __init__(self, behaviorManager):
		self.behaviorManager = behaviorManager
		self.logger = behaviorManager.logger
		self.timeout = 10 # seconds
		self.maxAngleError = 10 # degrees

	def init(self, bm):
		self.startTime = time.time()
		self.ball = bm.getTarget()
		self.framesNoBall = 0
		self.maxFramesNoBall = 3

	def execute(self, previousBehavior):
		output = PilotCommands(self.behaviorManager.lastArduinoInput)
		bm = self.behaviorManager.ballManager
		if (previousBehavior != self):
			self.init(bm)

		if bm.getTarget() != None:
			self.ball = bm.getTarget()
			self.framesNoBall = 0
		else:
			self.framesNoBall += 1
			if self.framesNoBall > self.maxFramesNoBall:
				return # lost the ball
		
		desiredDeltaAngle = utilities.angleCenterZero(self.ball.angle - self.behaviorManager.lastArduinoInput.heading)
		output.desiredDeltaAngle = desiredDeltaAngle

		output.rollerCommand = RollerCommands.FORWARD
		output.winchCommand = WinchCommands.DOWN
		output.rampCommand = RampCommands.UP

		return output

	def getPriority(self):
		return -1 if self.behaviorManager.ballManager.getTarget() == None else utilities.turnToBallPriority

class ApproachBall(Behavior):
	def __init__(self, behaviorManager):
		self.behaviorManager = behaviorManager
		self.logger = behaviorManager.logger
		self.forwardSpeed = 80
		self.timeout = 15 # seconds
		self.maxBallAngle = utilities.cameraFieldOfView/2 - 10 # this should be replaced with some reasonable empirically determined constant

	def init(self, ballCount):
		self.lastRunTime = None
		self.startTime = time.time()
		self.ballCount = ballCount

	def execute(self, previousBehavior):
		ai = self.behaviorManager.lastArduinoInput
		vi = self.behaviorManager.lastVisionInput
		bs = self.behaviorManager.behaviorStack
		bm = self.behaviorManager.ballManager
		output = PilotCommands(ai)

		output.rollerCommand = RollerCommands.FORWARD
		output.winchCommand = WinchCommands.DOWN
		output.rampCommand = RampCommands.UP

		if previousBehavior != self:
			self.init(bm.ballCount)

		t = time.time()

		if t-self.startTime > self.timeout:
			return None # TODO ensure that we don't try to approach the ball again
		if bm.ballCount > self.ballCount: # w00t, g0t b411
			return None
		ball = bm.getTarget()
		if ball == None:
			# lost the ball; hopefully this means that it is too close to us
			bs.append(DriveStraightAcquireBall(self.behaviorManager, self.ballCount))
			return None

		if self.lastRunTime:
			angle = utilities.angleCenterZero(ball.angle - ai.heading)
			self.logger.debug("Approaching ball at {0} degrees, {1} cm".format(angle, ball.distance))
			output.desiredDeltaAngle = angle
			output.forwardSpeed = self.forwardSpeed
		else:
			output = None
		self.lastRunTime = t


		return output

	def getPriority(self):
		ball = self.behaviorManager.ballManager.getTarget()
		if ball==None:
			return -1
		elif utilities.angleCenterZero(ball.angle - self.behaviorManager.lastArduinoInput.heading) > self.maxBallAngle:
			return -1
		else:
			return utilities.approachBallPriority
	
class DriveStraightAcquireBall(Behavior):
	def __init__(self, behaviorManager, ballCount):
		self.behaviorManager = behaviorManager
		self.forwardSpeed = 127
		self.ballCount = ballCount
		self.timeout = 3 # seconds

	def init(self):
		self.startTime = time.time()

	def execute(self):
		ai = self.behaviorManager.lastArduinoInput
		vi = self.behaviorManager.lastVisionInput
		bs = self.behaviorManager.behaviorStack
		bm = self.behaviorManager.ballManager
		output = PilotCommands(ai)

		pilotCommands.forwardSpeed = self.forwardSpeed

		if bm.ballCount > self.ballCount or time.time()-self.startTime > self.timeout:
			return None

		bs.append(self)

		output.rollerCommand = RollerCommands.FORWARD
		output.winchCommand = WinchCommands.DOWN
		output.rampCommand = RampCommands.UP

		return output

