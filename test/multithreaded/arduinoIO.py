# does arduino input and output it its own thread

import sys
sys.path.append("../..")
from stoppableThread import StoppableThread
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
	def __init__(self, leftDist=None, rightDist=None, startButton=None):
		self.leftDist = None # cm
		self.rightDist = None # cm
		self.startButton = None # boolean
		self.heading = None # angle in degrees

class ArduinoOutputData:
	def __init__(self, leftSpeed=0, rightSpeed=0):
		self.leftSpeed = leftSpeed
		self.rightSpeed = rightSpeed

class ArduinoThread(StoppableThread):
	def __init__(self):
		super(ArduinoThread, self).__init__("ArduinoIO")
	
	def safeInit(self):
		self.ard = arduino.Arduino()
		self.right = arduino.Motor(self.ard, 14, 42, 2) # arduino, current, direction, pwm
		self.left = arduino.Motor(self.ard, 15, 43, 3)
		self.irRight = arduino.AnalogInput(self.ard, 0) # arduino, pin
		self.irLeft = arduino.AnalogInput(self.ard, 1)
		self.startButton = arduino.DigitalInput(self.ard, 5) # arduino, pin number
		self.imu = arduino.IMU(self.ard) # arduino
		while True:
			self.ard.run()
			if self.ard.portOpened: # successfully connected
				break

	def safeRun(self):
		self.doInput()

		out = None
		while self.conn.poll():
			out = self.conn.recv()
		if out!=None:
			self.doOutput(out)

	def doInput(self):
		rightVal = self.irRight.getValue() 
		leftVal = self.irLeft.getValue()
		data = ArduinoInputData()
		if rightVal != None and leftVal != None:
			data.rightDist = getDistance(rightVal*5.0/1023)
			data.leftDist = getDistance(leftVal*5.0/1023)
			self.logger.debug("Left distance: {0}".format(data.leftDist))
			self.logger.debug("Right distance: {0}".format(data.rightDist))

		data.startButton = self.startButton.getValue()
		self.logger.debug("Start button: {0}".format(data.startButton))

		data.heading = self.imu.getRawValues()[0] # compass heading from (compass, accX, accY, accZ)
		self.logger.debug("Heading: {0}".format(data.heading))

		self.conn.send(data)

	def doOutput(self, out):
		if out != None:
			self.right.setSpeed(-int(out.rightSpeed))
			self.left.setSpeed(-int(out.leftSpeed))
			self.logger.debug("Left speed: {0}".format(out.leftSpeed))
			self.logger.debug("Right speed: {0}".format(out.rightSpeed))

	def cleanup(self):
		self.ard.stop()

