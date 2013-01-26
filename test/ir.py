import time
import sys
sys.path.append("..")

import arduino

# Example code to run an IR sensor.

ard = arduino.Arduino()  # Create the Arduino object
irRight = arduino.AnalogInput(ard, 0)  # Create an analog sensor on pin A0
irLeft = arduino.AnalogInput(ard, 1) 
ard.run()  # Start the thread which communicates with the Arduino

def getDistance(irVoltage):
	#See datasheet; there is a (mostly) linear relationship between voltage and (1/distance) for distances from 7 cm to 80 cm.
        if irVoltage < .3636:
                return 155 #readings are inaccurate below .3636 volts
	elif irVoltage > 2.982:
		return 7 #readings are inaccurate closer than 7 cm
	else: return 1.0 / ( .02554 + (irVoltage -.7321) * ((.1421-.02554)/(2.982-.7321)) )
	

try:
	# Main loop -- check the sensor
	while True:
		r = irRight.getValue()
		l = irLeft.getValue()
		if r!=None and l!=None:
			rightDist = getDistance(5.0/1024*r)
			leftDist  = getDistance(5.0/1024*l)
			rd = (6762/(r-9))-4
			ld = (6762/(l-9))-4
			print "{0}\t{1}\t\t{2}\t{3}\t\t{4}\t{5}".format(leftDist, rightDist, ld, rd, l, r)
		else:
			print "No reading"

		time.sleep(0.1)
except:
	ard.stop()
	raise
