#uses ball detection from cvTest and PID control to drive the robot towards balls

import sys
sys.path.append("..")
import time
import arduino

def getDistance(irVoltage):
        #See datasheet; there is a (mostly) linear relationship between voltage and (1/distance) for distances from 7 cm to 80 cm.
        if irVoltage < .7321:
                return 80 #readings are inaccurate after 80 cm
	elif irVoltage > 2.982:
		return 7 #readings are inaccurate closer than 7 cm
        else: 
		return 1.0 / ( .02554 + (irVoltage -.7321) * ((.1421-.02554)/(2.982-.7321)) )

class ArduinoInputData:
	def __init(self):
		self._leftDist = None
		self._rightDist = None
		self._startButton = None

class ArduinoInputThread(threading.Thread):
	def __init__(self, obj):
		self._stop = threading.Event()
		self._obj = obj
		threading.Thread.__init__(self)
	
	def stop(self):
		self._stop.set()

	def stopped(self):
		return self._stop.isSet()

	def run(self):
		while not self.stopped():
			try:
				ard = arduino.Arduino()
				right = arduino.Motor(ard, 14, 42, 2)
				left = arduino.Motor(ard, 15, 43, 3)
				irRight = arduino.AnalogInput(ard, 0) 
				irLeft = arduino.AnalogInput(ard, 1)
				startButton = arduino.DigitalInput(ard, 5) # arduino, pin number
				ard.run()

				while not stopped:
					try :
						rightVal = irRight.getValue() 
						leftVal = irLeft.getValue()
						data = ArduinoInputData()
						if rightVal != None and leftVal != None:
							data._rightDist = getDistance(rightVal*5.0/1023)
							data._leftDist = getDistance(leftVal*5.0/1023)
						data._startButton = startButton.getValue()
						obj.setObject(data)
					except(KeyboardInterrupt):
						self.stop()
						print "Arduino input thread exiting on keyboard interrupt"
					except:
						break
			except:
				print "Unknown Arduino error. Restarting arduino thread"
			finally:
				ard.stop()




		ard.stop()

