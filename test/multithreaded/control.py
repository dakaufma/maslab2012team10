from stoppableThread import StoppableThread
from arduinoIO import *
from pilot import *
from ball import *
import utilities
import time

class BehaviorManager(StoppableThread):
	"""Selects the robot's behavior (explore straight, approach ball, dump balls, etc) based on inputs, robot state, and time remaining in the game. The defaultBehaviors list contains all possible behaviors (it picks the highest priority behavior). If a behavior requires itself or another behavior to be run again it can add itself/other behaviors to the behaviorStack. Note that a behavior could be called indefinitely if it always added itself to the stack. After 3 minutes the BehaviorManager will stop the robot regardless of the contents of the behaviorStack."""

	def __init__(self, pilot, vision):
		super(BehaviorManager, self).__init__("BehaviorManager")
		self.pilot = pilot
		self.vision = vision

		self.defaultBehaviors = [DriveStraight(self), TurnToBall(self), ApproachBall(self)]
		self.behaviorStack = []

	def safeInit(self):
		self.previousBehavior = None
		self.lastVisionInput = None
		self.lastArduinoInput = None
		self.ballManager = BallManager()
		self.start = time.time()
		self.timeStackLastEmpty = time.time()
		self.maxTimeStackFilled = 30 # seconds

	def safeRun(self):
		# update input information from other processes
		self.ard.lock.acquire()
		while self.ard.otherConn.poll():
			self.lastArduinoInput = self.ard.otherConn.recv()
		self.ard.lock.release()
		self.vision.lock.acquire()
		while self.vision.conn.poll():
			self.lastVisionInput = self.vision.otherConn.recv()
		self.vision.lock.release()

		ballManager.update(self.lastVisionInput.balls)

		# select the next behavior
		if time.time()-self.start > 3*60: # Force the stop state when the match ends
			behavior = StopPermanently(self)
		elif not behaviorStack and time.time()-self.timeStackLastEmpty > self.maxTimeStackFilled: # If the stack has been occupied too long, assume something went wrong and reset stuff
			self.behaviorStack = []
			self.timeStackLastEmpty = time.time()
			behavior = ForcedMarch(self)
		elif len(behaviorStack) > 0: # take the next behavior off the stack
			behavior = behaviorStack.items.pop()
		else: # select the default state with the highest priority
			self.timeStackLastEmpty = time.time()
			behavior = None
			priority = None
			for b in defaultBehaviors:
				p = b.getPriority(self)
				if priority==None or p > priority:
					behavior = b
					priority = p

		# print behavior changes
		if self.previousBehavior != behavior:
			print "Changed behavior: {0}".format(behavior)
			self.logger.info("Changed states: {0}".format(behavior))

		# execute behavior 
		if behavior != None:
			output = behavior.execute(self.previousBehavior)
			if output != None:
				self.pilot.lock.acquire()
				self.pilot.otherConn.send(output)
				self.pilot.lock.release()

		self.previousBehavior = behavior

	def cleanup(self):
		pass

class Behavior:
	def execute(self, previousBehavior):
		"""Executes the code for this behavior (should take very little time). Returns the pilot commands"""
		raise NotImplementedError()

	def getPriority(self):
		return 0

class TurnToBall(Behavior):
	def __init__(self, behaviorManager):
		self.behaviorManager = behaviorManager
		self.logger = behaviorManager.logger
		self.timeout = 10 # seconds
		self.maxAngleError = 10 # degrees

	def init(bm):
		self.startTime = time.time()
		self.ball = bm.getTarget()

	def execute(self, previousBehavior):
		output = PilotCommands()
		bm = self.behaviorManager.ballManager
		if (previousBehavior != self):
			self.init(bm)

		if self.ball == None:
			return
		
		desiredAngleDelta = utilities.angleCenterZero(ball.angle - self.behaviorManager.lastArduinoInput.heading)
		output.desiredDeltaAngle = desiredDeltaAngle

		output.rollerCommand = RollerCommands.FORWARD
		output.winchCommand = WinchCommands.DOWN
		output.rampCommand = RampCommands.UP

		return output

	def getPriority(self):
		return -1 if self.behaviorManager.ballManager.getTarget() == None else utilites.turnToBallPriority

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
		self.ballcount = ballCount

	def execute(self, previousBehavior):
		output = PilotCommands()
		ai = self.behaviorManager.lastArduinoInput
		vi = self.behaviorManager.lastVisionInput
		bs = self.behaviorManager.behaviorStack
		bm = self.behaviorManager.ballManager

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

		output.rollerCommand = RollerCommands.FORWARD
		output.winchCommand = WinchCommands.DOWN
		output.rampCommand = RampCommands.UP

		return output

	def getPriority(self):
		ball = self.behaviorManager.ballManager.getTarget()
		if ball==None:
			return -1
		elif utilities.angleCenterZero(ball.angle - self.behaviorManager.lastArduinoInput.heading) > self.maxBallAngle:
			return -1
		else:
			return utilites.approachBallPriority
	
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
		ai = self.behaviorManager.lastArduinoInput
		vi = self.behaviorManager.lastVisionInput
		bs = self.behaviorManager.behaviorStack
		bm = self.behaviorManager.ballManager

		pilotCommands.forwardSpeed = self.forwardSpeed

		if bm.ballCount > self.ballCount or time.time()-self.startTime > self.timeout:
			return None

		bs.append(self)

		output.rollerCommand = RollerCommands.FORWARD
		output.winchCommand = WinchCommands.DOWN
		output.rampCommand = RampCommands.UP

		return output

class DriveStraight(Behavior):
	"""Goes forward. Can change states to track a ball or avoid a wall"""

	def __init__(self, behaviorManager):
		self.behaviorManager = behaviorManager
		self.logger = behaviorManager.logger
		self.forwardSpeed = 127
		self.minDist = 25 # cm

	def execute(self, previousBehavior):
		ai = self.behaviorManager.lastArduinoInput
		vi = self.behaviorManager.lastVisionInput
		bs = self.behaviorManager.behaviorStack
		bm = self.behaviorManager.ballManager

		if utilities.crashed(ai):
			bs.append(Uncrash(self.behaviorManager))
		elif utilities.nearWall(ai):
			bs.append(AvoidWall(self.behaviorManager))


		output = PilotCommands()
		output.forwardSpeed = self.forwardSpeed
		output.rollerCommand = RollerCommands.FORWARD
		output.winchCommand = WinchCommands.DOWN
		output.rampCommand = RampCommands.UP

		return output

class AvoidWall(Behavior):
	def __init__(self, behaviorManager):
		self.behaviorManager = behaviorManager
		self.logger = behaviorManager.logger
		self.turnSpeed = 127
		self.forwardSpeed = 127
		self.minDist = utilities.nearWallDist
		self.logger = logger

	def execute(self, previousBehavior):
		output = PilotCommands()
		ai = self.behaviorManager.lastArduinoInput
		vi = self.behaviorManager.lastVisionInput
		bs = self.behaviorManager.behaviorStack
		bm = self.behaviorManager.ballManager

		if utilities.crashed(ai):
			bs.append(self)
			bs.append(Uncrash(self.behaviorManager))
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
	def __init__(self, behaviorManager):
		self.behaviorManager = behaviorManager
		self.logger = behaviorManager.logger
		self.forwardSpeed = 127
		self.turnSpeed = 80

	def init(ai):
		self.crashedRight = ai.frBump or ai.brBump
		self.crashedLeft = ai.flBump or ai.blBump
		self.crashedFront = ai.frBump or flBump
		self.crashedBack = ai.brBump or blBump

	def execute(self, previousBehavior):
		output = PilotCommands()
		ai = self.behaviorManager.lastArduinoInput
		vi = self.behaviorManager.lastVisionInput
		bs = self.behaviorManager.behaviorStack
		bm = self.behaviorManager.ballManager
		
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

