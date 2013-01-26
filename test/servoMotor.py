import sys
sys.path.append("..")
import time

import arduino

# testing using a servo modded to be a motor

ard = arduino.Arduino()
servo = arduino.Servo(ard, 11)  # Create a Servo object
ard.run()  # Run the Arduino communication thread

try:
	while True:
		print "Forward"
		servo.setAngle(120)
		time.sleep(2)
		    
		print "Reverse"
		servo.setAngle(0)
		time.sleep(2)

		print "Stop"
		servo.setAngle(94)
		time.sleep(2)
		    
except:
	servo.setAngle(94)
	ard.stop()
	print "done"
