def nearWall(arduinoInput):
	return arduinoInput != None and (arduinoInput.leftDist < nearWallDist or arduinoInput.rightDist < nearWallDist)

def crashed(arduinoInput):
	return arduinoInput.frBump or arduinoInput.flBump or arduinoInput.brBump or arduinoInput.blBump

def angleCenterZero(angle):
	"""Given an angle in degrees, returns the same angle in the range (-180, 180)"""
	angle = angle % 360
	if angle > 180:
		angle -= 360
	if angle <= -180:
		angle += 360
	return angle

# Constants
cameraFieldOfView = 78 # degrees
nearWallDist = 20 # cm

turnToBallPriority = 5
approachBallPriority = 6
approachYellowWallPriority = 10
