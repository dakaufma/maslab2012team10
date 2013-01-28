
class Ball:
	def __init__(self, angle=None, isRed=None, lastTimeSeen=None, distance=None):
		self.angle = angle
		self.distance = distance
		self.isRed = isRed
		self.lastTimeSeen = lastTimeseen
		self.onCamera = True


class BallManager:
	def __init__(self):
		self.ballCount = 0

	def getTarget():
		raise NotImplementedError()

	def forget(self, ball):
		raise NotImplementedError()

	def update(self, balls):
		raise NotImplementedError()
