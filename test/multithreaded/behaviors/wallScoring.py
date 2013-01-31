import sys
sys.path.append("..")
import utilities
from behavior import Behavior
from movement import ForcedMarch
from scoring import LiftBasket
from pilot import *
import time

class ApproachYellowWall(Behavior):
	def __init__(self, behaviorManager):
		self.behaviorManager = behaviorManager
		self.logger = behaviorManager.logger
		self.distThresh = 30 # cm
		self.slowForwardSpeed = 60
		self.fastForwardSpeed = 100
		self.irSpacing = 30.5 # cm between the IR sensors
		self.timeout = 15 # seconds

	def init(self):
		self.wall = self.behaviorManager.wallManager.getTarget()
		self.startTime = time.time()

	def execute(self, previousBehavior):
		bm = self.behaviorManager
		wm = bm.wallManager
		ai = bm.lastArduinoInput
		bs = bm.behaviorStack

		if previousBehavior != self:
			self.init()
		if self.wall == None:
			return # no wall to approach
		if wm.getTarget() != None:
			self.wall = wm.getTarget() # update wall data

		if ai.flBump or ai.frBump: # we made it to the wall
			bs.append(LiftBasket(bm))
		elif time.time() - self.startTime > self.timeout: #timed out; abort
			bs.append(ForcedMarch(bm))
			return
		else:
			bs.append(self)

		output = PilotCommands()
		output.rollerCommand = RollerCommands.FORWARD
		output.winchCommand = WinchCommands.DOWN
		output.rampCommand = RampCommands.UP
		
		if ai.leftDist < self.distThresh and ai.rightDist < self.distThresh:
			# use IR sensors to determine angle relative to the wall, turn perpendicular to it
			# also move forward less quickly
			output.forwardSpeed = self.slowForwardSpeed
			output.desiredDeltaAngle = 180/3.14159*math.atan((ai.leftDist - ai.rightDist)/self.irSpacing)
		else:
			# use camera information for angle
			# move quickly
			output.forwardSpeed = self.fastForwardSpeed
			output.desiredDeltaAngle = self.wall.angle
	
	def getPriority(self):
		if self.behaviorManager.ballManager.ballCount == 0:
			return -1
		if self.behaviorManager.wallManager.getTarget() == None:
			return -1
		return utilites.approachYellowWallPriority

