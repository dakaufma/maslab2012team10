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
		self.leftDist = None
		self.rightDist = None
		self.startButton = None

class ArduinoOutputData:
	def __init__(self, leftSpeed=0, rightSpeed=0):
		self.leftSpeed = leftSpeed
		self.rightSpeed = rightSpeed

class ArduinoThread(StoppableThread):
	"""Thread responsible for both input and output. Arduino[Input/Output]Data objects are stored in SharedObjects in the inputObj and outputObj fields"""
	def __init__(self):
		super(ArduinoThread, self).__init__()
		self.name = "ArduinoIO"
	
	def safeInit(self):
		self.ard = arduino.Arduino()
		self.right = arduino.Motor(self.ard, 14, 42, 2)
		self.left = arduino.Motor(self.ard, 15, 43, 3)
		self.irRight = arduino.AnalogInput(self.ard, 0) 
		self.irLeft = arduino.AnalogInput(self.ard, 1)
		self.startButton = arduino.DigitalInput(self.ard, 5) # arduino, pin number
		self.ard.run()

	def safeRun(self):
		self.doInput()

		# if there is output ready, do output
		# Note that output is rate-limited by input rate, but this should be ok
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
		data.startButton = self.startButton.getValue()


		self.conn.send(data)

	def doOutput(self, out):
		if out and out.rightSpeed and out.leftSpeed:
			self.right.setSpeed(-int(out.rightSpeed))
			self.left.setSpeed(-int(out.leftSpeed))

	def cleanup(self):
		self.ard.stop()

