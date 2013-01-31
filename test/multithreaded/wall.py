import math
import utilities

class Wall:
	def __init__(self, angle, x, y, width, height, area):
		self.angle = angle
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.area = area

class WallManager:
	def __init__(self):
		self.walls = []
		self.target = None
		self.noTargetFrameCount = 0
		self.maxFrames = 3

	def getTarget():
		if self.noTargetFrameCount <= self.maxFrames:
			return self.target
		else:
			return None

	def update(self, walls):
		self.walls = walls

		# Pick a wall to target (the one with the most pixels)
		best = None
		for wall in self.walls:
			if best==None or wall.area > best.area:
				best = wall

		# If we haven't found a new target, keep the old one
		if best == None:
			self.noTargetFrameCount += 1
		else:
			self.noTargetFrameCount = 0
			self.target = best

