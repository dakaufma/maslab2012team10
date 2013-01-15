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


MIN_DIST = 15 #cm

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

		pid = PID(1.0, 0, 0, 1000, -1000, 127, -127)
		pidLastTime = 0
		forwardSpeed = 100
		maxAngleError = 15
		currentlyTurning = False
		currentlyAvoidingWall = False
		camera.read(); # guessing that the first call to read() takes a few seconds and that subsequent ones are fast --> call it now before the timer starts

		#wait for a falling edge on the start button
		previousStartVal = False
		startVal = False
		while (not (previousStartVal and not startVal)):
			previousStartVal = startVal
			startVal = startButton.getValue()

		startTime = time.time()

		while time.time() - startTime < 3 * 60:
			f,img = camera.read();

			leftSpeed = rightSpeed = forwardSpeed
			if not currentlyAvoidingWall: #don't process images while aoviding walls; it slows code down too much. TODO use threads
				print "not avoiding a wall"
				if smallImg==None:
					smallImg = numpy.zeros((img.shape[0]*scale, img.shape[1]*scale, img.shape[2]), numpy.uint8)

				cv2.resize(img, None, smallImg, .25, .25)

				hsv, hue, sat, val, redDist, redMaskedDist, redImg, redMask, redMask1, redMask2, redBalls, greenBalls = processImg(smallImg, hsv, hue, sat, val, redDist, redMaskedDist, redImg, redMask, redMask1, redMask2, distThreshold, minArea)

				for ball in redBalls:
					greenBalls.append(ball) # temporary code to just detect all balls the same way

				#vision --> follow balls
				if len(greenBalls) > 0:
					print "found a ball"
					closestBall = None
					for ball in greenBalls:
						if closestBall == None or ball[3] > closestBall[3]: # index 3 is radius; TODO make ball a class so you can refer to attributes by name
							closestBall = ball

					angle = ball[0]
					if angle < maxAngleError: #lined up enough; just approach straight
						rightSpeed = forwardSpeed
						leftSpeed = forwardSpeed
					else: #too far out of line; turn in place to line up
						if not currentlyTurning:
							pid.reset()
							pidLastTime = time.time()
							#don't change right speed or left speed until the next iteration, when we have a delta t
						else:
							pidCurrentTime = time.time()
							output = pid.run(angle, pidCurrentTime - pidLastTime)
							pidLastTime = pidCurrentTime
							rightSpeed = output
							leftSpeed = output
							print str(int(output)) + "\t" + str(angle)

			#avoid walls
			rightVal = irRight.getValue() 
			leftVal = irLeft.getValue()
			if rightVal != None and leftVal != None:
				rightDist = getDistance(rightVal*5.0/1023)
				leftDist = getDistance(leftVal*5.0/1023)
				
				if rightDist < MIN_DIST:
					print "avoiding a wall; right side\t" + str(rightDist)
					currentlyAvoidingWall = True
					rightSpeed = 0
					leftSpeed = -127
				elif leftDist < MIN_DIST:
					print "avoiding a wall; left side\t" + str(leftDist)
					currentlyAvoidingWall = True
					rightSpeed = -127
					leftSpeed = 0
				else:
					currentlyAvoidingWall = False
					print "not avoiding a wall"
				
			else:
				leftSpeed = rightSpeed = 0
				print "no reading"
			print str(rightSpeed) + "\t" + str(leftSpeed)
			right.setSpeed(rightSpeed)
			left.setSpeed(leftSpeed)

			key = cv2.waitKey(1)
			if key == 113: # press 'q' to exit
				break
			elif key == 112: # press 'p' to pause
				key = 0
				while key != 112 and key != 113: # press 'p' again to resume; 'q' still quits
					key = cv2.waitKey(0)
				if key == 113:
					break
	finally:
		right.setSpeed(0)
		left.setSpeed(0)
		time.sleep(.1) # not sure this is necessary, but delay before cutting arduino communication
		ard.stop()

