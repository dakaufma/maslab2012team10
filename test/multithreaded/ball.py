import math
import utilities

class Ball:
	def __init__(self, angle=None, isRed=None, lastTimeSeen=None, distance=None):
		self.angle = angle
		self.distance = distance
		self.isRed = isRed
		self.lastTimeSeen = lastTimeSeen

class BallManager:
	def __init__(self):
		self.ballCount = 0
		self.balls = []
		self.target = None
		self.noTargetFrameCount = 0
		self.maxFrames = 3

	def getTarget():
		if self.noTargetFrameCount <= self.maxFrames:
			return self.target
		else:
			return None

	def dumpAll(self):
		self.ballCount = 0

	def acquiredBall(self):
		self.ballCount += 1

	def update(self, balls):
		self.balls = balls

		# Pick a ball to target
		# Just pick the closest one; it's possible that a group will appear close even though it isn't, but then at least you're targetting a group of balls
		best = None
		for ball in self.balls:
			if best==None or ball.distance < best.distance:
				best = ball

		# If we haven't found a new target, keep the old one
		if best == None:
			self.noTargetFrameCount += 1
		else:
			self.noTargetFrameCount = 0
			self.target = best

