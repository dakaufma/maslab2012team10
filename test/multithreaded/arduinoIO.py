# does arduino input and output it its own thread

import sys
sys.path.append("../..")
from stoppableThread import StoppableThread
import time
import arduino

def getDistance(irVoltage):
        #See datasheet; there is a (mostly) linear relationship between voltage and (1/distance) for distances from 7 cm to 80 cm.
        if irVoltage < .3636:
                return 155 #readings are inaccurate below .3636 volts
	elif irVoltage > 2.982:
		return 7 #readings are inaccurate closer than 7 cm
        else: 
		return 1.0 / ( .02554 + (irVoltage -.7321) * ((.1421-.02554)/(2.982-.7321)) )

class ArduinoInputData:
	def __init__(self, leftDist=None, rightDist=None, startButton=None, heading=None, frBump=None, flBump=None, brBump=None, blBump=None, winchBottom=None, winchTop=None):
		self.leftDist = leftDist # cm
		self.rightDist = rightDist # cm
		self.startButton = startButton # boolean
		self.heading = heading # angle in degrees
		self.frBump = frBump # True/false bumped into something
		self.flBump = flBump
		self.brBump = brBump
		self.blBump = blBump
		self.winchBottom = winchBottom
		self.winchTop = winchTop

class ArduinoOutputData:
	def __init__(self, leftSpeed=0, rightSpeed=0, rollerCommand=0, winchCommand=0, rampAngle=0):
		self.leftSpeed = leftSpeed
		self.rightSpeed = rightSpeed
		self.rollerCommand = rollerCommand
		self.winchCommand = winchCommand
		self.rampAngle = rampAngle

class ArduinoThread(StoppableThread):
	def __init__(self):
		super(ArduinoThread, self).__init__("ArduinoIO")
	
	def safeInit(self):
		self.ard = arduino.Arduino()
		self.right = arduino.Motor(self.ard, 14, 42, 2) # arduino, current, direction, pwm
		self.left = arduino.Motor(self.ard, 15, 43, 3)
		self.winch = arduino.Motor(self.ard, 16, 44, 4)
		self.roller = arduino.Motor(self.ard, 17, 45, 5)
		self.ramp = arduino.Servo(self.ard, 6)
		self.irRight = arduino.AnalogInput(self.ard, 0) # arduino, pin
		self.irLeft = arduino.AnalogInput(self.ard, 1)
		self.startButton = arduino.DigitalInput(self.ard, 5) # arduino, pin number
		self.imu = arduino.IMU(self.ard) # arduino
		self.frBump = arduino.DigitalInput(self.ard, 10)
		self.flBump = arduino.DigitalInput(self.ard, 11)
		self.brBump = arduino.DigitalInput(self.ard, 12)
		self.blBump = arduino.DigitalInput(self.ard, 13)
		self.winchTop = arduino.DigitalInput(self.ard, 14)
		self.winchBottom = arduino.DigitalInput(self.ard, 15)

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

		data.frBump = self.frBump.getValue()
		data.flBump = self.flBump.getValue()
		data.brBump = self.brBump.getValue()
		data.blBump = self.blBump.getValue()

		self.conn.send(data)

	def doOutput(self, out):
		if out != None:
			self.right.setSpeed(-int(out.rightSpeed))
			self.left.setSpeed(-int(out.leftSpeed))
			#self.winch.setSpeed(int(out.winchSpeed))
			#self.roller.setSpeed(int(out.rollerSpeed))
			#self.ramp.setAngle(int(out.rampAngle))
			self.logger.debug("Left speed: {0}".format(out.leftSpeed))
			self.logger.debug("Right speed: {0}".format(out.rightSpeed))
			self.logger.debug("Winch speed: {0}".format(out.winchSpeed))
			self.logger.debug("Roller speed: {0}".format(out.rollerSpeed))
			self.logger.debug("Ramp angle: {0}".format(out.rampAngle))

	def cleanup(self):
		self.ard.stop()

