nearWallDist = 20 # cm
def nearWall(arduinoInput):
	return arduinoInput != None and (arduinoInput.leftDist < nearWallDist or arduinoInput.rightDist < nearWallDist)

def crashed(arduinoInput):
	raise NotImplementedError()

def angleCenterZero(angle):
	"""Given an angle in degrees, returns the same angle in the range (-180, 180)"""
	angle = angle % 360
	if angle > 180:
		angle -= 360
	if angle <= -180:
		angle += 360
	return angle

