import sys
sys.path.append("..")
import time

import arduino

sleepTime = 2

ard = arduino.Arduino()
right = arduino.Motor(ard, 14, 42, 2) #(arduino, currentPin, directionPin, pwmPin)
left = arduino.Motor(ard, 15, 43, 3)
ard.run()  # Start the Arduino communication thread

while True:
	for s in range(0, 127, 10):
		print s
		left.setSpeed(s)
		right.setSpeed(s)
		time.sleep(sleepTime)
	print "stop"
	left.setSpeed(0)
	right.setSpeed(0)
	time.sleep(sleepTime)

