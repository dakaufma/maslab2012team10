from stoppableThread import StoppableThread
from ball import BallManager
from wall import WallManager
from behaviors.movement import *
from behaviors.ballFollowing import *
from behaviors.wallScoring import *
import time

class BehaviorManager(StoppableThread):
	"""Selects the robot's behavior (explore straight, approach ball, dump balls, etc) based on inputs, robot state, and time remaining in the game. The defaultBehaviors list contains all possible behaviors (it picks the highest priority behavior). If a behavior requires itself or another behavior to be run again it can add itself/other behaviors to the behaviorStack. Note that a behavior could be called indefinitely if it always added itself to the stack. After 3 minutes the BehaviorManager will stop the robot regardless of the contents of the behaviorStack."""

	def __init__(self, ard, pilot, vision):
		super(BehaviorManager, self).__init__("BehaviorManager")
		self.ard = ard
		self.pilot = pilot
		self.vision = vision

		self.defaultBehaviors = [DriveStraight(self), TurnToBall(self), ApproachBall(self), ApproachYellowWall(self)]
		self.behaviorStack = []

	def safeInit(self):
		self.previousBehavior = None
		self.lastVisionInput = None
		self.lastArduinoInput = None
		self.ballManager = BallManager()
		self.wallManager = WallManager()
		self.start = time.time()
		self.timeStackLastEmpty = time.time()
		self.maxTimeStackFilled = 30 # seconds

		#ensure that we have some input from other processes
		self.ard.lock.acquire()
		while True:
			self.lastArduinoInput = self.ard.otherConn.recv()
			if not self.ard.otherConn.poll():
				break
		self.ard.lock.release()
		self.vision.lock.acquire()
		while True:
			self.lastVisionInput = self.vision.otherConn.recv()
			if not self.vision.conn.poll():
				break
		self.vision.lock.release()

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

		self.ballManager.update(self.lastVisionInput.balls)
		self.wallManager.update(self.lastVisionInput.walls)

		# select the next behavior
		if time.time()-self.start > 3*60: # Force the stop state when the match ends
			behavior = StopPermanently(self)
		elif not self.behaviorStack and time.time()-self.timeStackLastEmpty > self.maxTimeStackFilled: # If the stack has been occupied too long, assume something went wrong and reset stuff
			self.behaviorStack = []
			self.timeStackLastEmpty = time.time()
			behavior = ForcedMarch(self)
		elif len(self.behaviorStack) > 0: # take the next behavior off the stack
			behavior = self.behaviorStack.pop()
		else: # select the default state with the highest priority
			self.timeStackLastEmpty = time.time()
			behavior = None
			priority = None
			for b in self.defaultBehaviors:
				p = b.getPriority()
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

