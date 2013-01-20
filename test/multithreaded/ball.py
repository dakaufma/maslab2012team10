
class Ball:
	def __init__(self, angle=None, isRed=None, time=None, distance=None):
		self.angle = angle
		self.distance = distance
		self.isRed = isRed
		self.time = time

	def setDistance(self, dist):
		self.distance = dist

	def getDistance(self):
		return self.distance

	def setAngle(self, ang):
		self.angle = ang

	def getAngle(self):
		return self.angle

	def setRed(self, isRed):
		self.isRed = isRed

	def isRed(self):
		return self.isRed

	def getTime(self):
		return self.time

	def setTime(self, t):
		self.time = t
