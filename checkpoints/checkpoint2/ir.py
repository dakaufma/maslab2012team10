import time
import sys
sys.path.append("../..")

import arduino

# Example code to run an IR sensor.

ard = arduino.Arduino()  # Create the Arduino object
irRight = arduino.AnalogInput(ard, 0)  # Create an analog sensor on pin A0
irLeft = arduino.AnalogInput(ard, 1) 
rightMotor = arduino.Motor(ard, 14, 42, 2) #(arduino, currentPin, directionPin, pwmPin)
leftMotor = arduino.Motor(ard, 15, 43, 3)
ard.run()  # Start the thread which communicates with the Arduino

def getDistance(irVoltage):
	#See datasheet; there is a (mostly) linear relationship between voltage and (1/distance) for distances from 7 cm to 80 cm.
	if irVoltage < .7321:
		return 80 #readings are inaccurate after 80 cm
	elif irVoltage > 2.982:
		return 7 #readings are inaccurate closer than 7 cm
	else: return 1.0 / ( .02554 + (irVoltage -.7321) * ((.1421-.02554)/(2.982-.7321)) )
	

MIN_DIST = 20 #cm

# Main loop -- check the sensor and update the digital output
while True:
	rightVal = irRight.getValue() 
	leftVal = irLeft.getValue()
	leftSpeed = rightSpeed = 0

	if rightVal != None and leftVal != None:
		rightDist = getDistance(rightVal*5.0/1023)
		leftDist = getDistance(leftVal*5.0/1023)
		
		leftSpeed = rightSpeed = 127
		if rightDist < MIN_DIST:
			rightSpeed = 0
			leftSpeed = -127
		elif leftDist < MIN_DIST:
			rightSpeed = -127
			leftSpeed = 0
		
	else:
		leftSpeed = rightSpeed = 0
		print "no reading"
	
	rightMotor.setSpeed(rightSpeed)
	leftMotor.setSpeed(leftSpeed)

	time.sleep(0.1)
