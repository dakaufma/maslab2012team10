import math
import utilities

class Ball:
	def __init__(self, angle=None, isRed=None, lastTimeSeen=None, distance=None):
		self.angle = angle
		self.distance = distance
		self.isRed = isRed
		self.lastTimeSeen = lastTimeSeen
		self.numFramesSeen = 1
		self.framesUnseenCenteredInView = 0

class BallManager:
	def __init__(self):
		self.ballCount = 0
		self.redCount = 0
		self.greenCount = 0
		self.unknownCount = 0
		self.numRedSeen = 0
		self.numGreenSeen = 0
		self.maxBallAge = 15 # seconds without seeing the ball before forgetting about it
		self.minBallFrames = 3
		self.maxFramesUnseenCenteredInView = 3
		self.balls = []
		self.potentialBalls = []
		self.pursuingBall = False
		self.lastTarget = None

	def getTarget():
		if self.lastTarget != None:
			return self.lastTarget

		# for now just pick the closest one; it's possible that a group will appear close even though it isn't, but then at least you're targetting a group of balls
		best = None
		for ball in self.balls:
			if best==None or ball.distance < best.distance:
				best = ball

		self.lastTarget = best
		return best

	def matches(self, b, ball):
		return math.abs(utilities.centerAngleZero(b.angle - ball.angle)) < 5 and math.abs(b.distance - ball.distance) < 2 # angle within x degrees and distance within y inches

	def forget(self, ball):
		try:
			balls.remove(ball)
		except ValueError:
			pass
		try:
			potentialBalls.remove(ball)
		except ValueError:
			pass

	def dumpAll(self):
		self.ballCount = 0
		self.redCount = 0
		self.greenCount = 0

	def acquiredBall(self):
		self.ballCount += 1
		ball = self.getTarget() # assume the acquired ball was the one we wanted to target
		if ball == None: # we just acquired an unknown ball
			self.unknownCount += 1
		else:
			if ball.isRed:
				self.redCount += 1
			else:
				self.greenCount += 1
		self.forget(self.getTarget()) # assume it was the ball we wanted to target
		self.lastTarget = None

	def update(self, balls, heading, pursuingBall):
		self.pursuingBall = pursingBall
		if not pursuingBall:
			self.lastTarget = None # no need to remember the previous target; no one is pursuing it
		else:
			self.getTarget() # pick a target for them to pursue

		# Increase the frame count for balls that should be centered in the camera's view
		for ball in balls:
			if self.centeredInView(ball, heading):
				ball.numFramesUnseenCenteredInView += 1
			else:
				ball.numFramesUnseenCenteredInView = 0

		# Look for known balls that are likely the detected balls and update them
		# if no matches are found assume the detected ball is a ball we haven't seen before
		confirmedPotentialBalls = []
		for ball in balls:
			matched = False
			for b in self.balls:
				if self.matches(ball, b):
					matched = True
					b.angle = ball.angle
					b.distance = ball.distance
					b.lastTimeSeen = ball.lastTimeSeen
					b.numFramesSeen += 1
					b.numFramesUnseenCenteredInView = 0
					break
			if not matched: # try matching against the potential balls
				for b in self.potentialBalls:
					if self.matches(ball, b):
						matched = True
						b.angle = ball.angle
						b.distance = ball.distance
						b.lastTimeSeen = ball.lastTimeSeen
						b.numFramesSeen += 1
						b.numFramesUnseenCenteredInView = 0
						confirmedPotentialBalls.append(b)
						break
			if not matched: # found a new potential ball
				confirmedPotentialBalls.append(ball)

		# Clear all records of potential balls that we didn't see this frame
		self.potentialBalls = confirmedPotentialBalls

		# If a potential ball has been seen for enough consecutive frames it is a ball
		for b in self.potentialBalls:
			if b.numFramesSeen >= self.minBallFrames:
				self.potentialBalls.remove(b)
				self.balls.append(b)

		# If a ball hasn't been seen in a long time, forget it
		for b in self.balls:
			if now - b.lastTimeSeen > self.maxBallAge:
				if self.lastTarget != b: # don't forget the ball we're targetting
					self.balls.remove(b)

		# If a ball should be centered in the camera's view but hasn't been seen for n frames, forget it
		for b in self.balls:
			if ball.numFramesUnseenCenteredInView > self.maxFramesUnseenCenteredInView:
				if self.lastTarget != b: # don't forget the ball we're targetting
					self.balls.remove(b)

	def centeredInView(ball, heading):
		angle = utilities.angleCenterZero(heading-ball.angle)
		return math.abs(angle) < 15 # degrees; empirically determined

