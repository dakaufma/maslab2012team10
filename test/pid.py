#!/usr/bin/python

#uses ball detection from cvTest and PID control to drive the robot towards balls

from cvTest import processImg
from discretePID import PID
import cv2
import numpy
import sys
sys.path.append("..")
import time
import arduino

redHue = 0
redHueMin = 170
redHueMax = 15
redSat = 255
redVal = 255

greenHue = 60
greenHueMin = 45
greenHueMax = 75
greenSat = 255
greenVal = 255


MIN_DIST = 25 #cm

def getDistance(irVoltage):
        #See datasheet; there is a (mostly) linear relationship between voltage and (1/distance) for distances from 7 cm to 80 cm.
        if irVoltage < .7321:
                return 80 #readings are inaccurate after 80 cm
	elif irVoltage > 2.982:
		return 7 #readings are inaccurate closer than 7 cm
        else: 
		return 1.0 / ( .02554 + (irVoltage -.7321) * ((.1421-.02554)/(2.982-.7321)) )

if __name__ == '__main__':
	ard = arduino.Arduino()
	right = arduino.Motor(ard, 14, 42, 2)
	left = arduino.Motor(ard, 15, 43, 3)
	irRight = arduino.AnalogInput(ard, 0)  # Create an analog sensor on pin A0
	irLeft = arduino.AnalogInput(ard, 1)
	arduino.DigitalOutput(ard, 5).setValue(0)
	startButton = arduino.DigitalInput(ard, 5) # arduino, pin number
	ard.run()

	try:
		hsv = hue = sat = val = redDist = redMaskedDist = redImg = redMask = redMask1 = redMask2 = None
		#read images from the camera
		camera = cv2.VideoCapture(1);
		smallImg = None
		scale = .25
		distThreshold = 80 # empirically determined
		minArea = 25 # empirically determined

		pid = PID(1.0, .1, 0, 500, -500, 127, -127)
		pidLastTime = 0
		searchSpeed = 127
		approachSpeed = 80
		currentlyTurning = False
		currentlyAvoidingWall = False

		#wait for a falling edge on the start button
		previousStartVal = False
		startVal = False
		print "Press the button to start"
		while (not (previousStartVal and not startVal)):
			previousStartVal = startVal
			startVal = startButton.getValue()
			time.sleep(.1)

		startTime = time.time()

		while time.time() - startTime < 3 * 60:
			debugStr = ""

			f,img = camera.read();

			leftSpeed = rightSpeed = searchSpeed
			if not currentlyAvoidingWall: #don't process images while aoviding walls; it slows code down too much. TODO use threads
				if smallImg==None:
					smallImg = numpy.zeros((img.shape[0]*scale, img.shape[1]*scale, img.shape[2]), numpy.uint8)

				cv2.resize(img, None, smallImg, .25, .25)

				hsv, hue, sat, val, redDist, redMaskedDist, redImg, redMask, redMask1, redMask2, redBalls, greenBalls = processImg(smallImg, hsv, hue, sat, val, redDist, redMaskedDist, redImg, redMask, redMask1, redMask2, distThreshold, minArea)

				for ball in redBalls:
					greenBalls.append(ball) # temporary code to just detect all balls the same way

				#vision --> follow balls
				if len(greenBalls) > 0:
					debugStr += "found a ball\t"
					closestBall = None
					for ball in greenBalls:
						if closestBall == None or ball[3] > closestBall[3]: # index 3 is radius; TODO make ball a class so you can refer to attributes by name
							closestBall = ball

					angle = ball[0]
					debugStr += str(angle) +"\t"
					if not currentlyTurning:
						pid.reset()
						pidLastTime = time.time()
						#don't change right speed or left speed until the next iteration, when we have a delta t
					else:
						pidCurrentTime = time.time()
						pidOutput = int(pid.run(angle, pidCurrentTime - pidLastTime))
						pidLastTime = pidCurrentTime
						rightSpeed = approachSpeed - pidOutput
						leftSpeed = approachSpeed + pidOutput
						tmp = max(abs(leftSpeed), abs(rightSpeed), 127)
						leftSpeed = leftSpeed*127/tmp
						rightSpeed = rightSpeed*127/tmp
						debugStr += str(int(pidOutput)) + "\t" + str(angle) + "\t"
					currentlyTurning = True
				else:
					currentlyTurning = False

			#avoid walls
			rightVal = irRight.getValue() 
			leftVal = irLeft.getValue()
			if rightVal != None and leftVal != None:
				rightDist = getDistance(rightVal*5.0/1023)
				leftDist = getDistance(leftVal*5.0/1023)
				
				if rightDist < MIN_DIST:
					debugStr += "avoiding a wall; right side\t" + str(rightDist) + "\t"
					currentlyAvoidingWall = True
					rightSpeed = 40
					leftSpeed = -127
				elif leftDist < MIN_DIST:
					debugStr += "avoiding a wall; left side\t" + str(leftDist) + "\t"
					currentlyAvoidingWall = True
					rightSpeed = -127
					leftSpeed = 40
				else:
					currentlyAvoidingWall = False
			else:
				leftSpeed = rightSpeed = 0
				debugStr+= "no reading\t"
			debugStr += str(rightSpeed) + "\t" + str(leftSpeed)

			#print debugStr
			right.setSpeed(-rightSpeed)
			left.setSpeed(leftSpeed)

	finally:
		right.setSpeed(0)
		left.setSpeed(0)
		time.sleep(.1) # not sure this is necessary, but delay before cutting arduino communication
		ard.stop()

