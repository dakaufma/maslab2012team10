import sys
sys.path.append("..")
import time

import arduino

sleepTime = 2

ard = arduino.Arduino()
right = arduino.Motor(ard, 11, 53, 41) #(arduino, currentPin, directionPin, pwmPin)
left = arduino.Motor(ard, 10, 37, 35)
ard.run()  # Start the Arduino communication thread

while True:
	print "forward"
	right.setSpeed(127)
#	left.setSpeed(127)
	time.sleep(sleepTime)
	print "stop"
	right.setSpeed(0)
#	left.setSpeed(0)
	time.sleep(sleepTime)
	print "back"
	right.setSpeed(-127)
#	left.setSpeed(-127)
	time.sleep(sleepTime)
	print "stop"
	right.setSpeed(0)
#	left.setSpeed(0)
	time.sleep(sleepTime)
