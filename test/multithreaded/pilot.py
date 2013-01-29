from discretePID import PID
from stoppableThread import StoppableThread
from arduinoIO import *
import utilities
import time

class RollerCommands:
	STOP, FORWARD, REVERSE = range(3)

class WinchCommands:
	STOP, DOWN, HALF, UP = range(4)

class RampCommands:
	STOP, UP, DOWN = range(3)

class PilotCommands:
	def __init__(self, forwardSpeed=0, desiredDeltaAngle=None, turnSpeed=0, rollerCommand=RollerCommands.STOP, winchCommand=WinchCommands.STOP, rampCommand=RampCommands.STOP):
		# Drive commands: forwardSpeed and one type of angular control should be non-None
		self.forwardSpeed = forwardSpeed
		self.desiredDeltaAngle = desiredDeltaAngle
		self.turnSpeed = turnSpeed

		# Roller command
		self.rollerCommand = rollerCommand

		# Winch command
		self.winchCommand = winchCommand

		# Ramp command
		self.rampCommand = rampCommand

		# dead man's switch to stop the robot
		self.lastTimeCommandReceived = time.time()
		self.deadManTimeout = 1 # second

class Pilot(StoppableThread):
	"""Translates higher level navigation commands (e.g. turn to a certain angle, pull the winch up, etc) into arduino-level output"""

	def __init__(self, ard):
		super(Pilot, self).__init__("Pilot")
		self.ard = ard

	def safeInit(self):
		self.lastPIDtime = None
		self.rampUpAngle = 90
		self.rampDownAngle = 0
		self.rampLastAngle = self.rampUpAngle
		self.lastTimeCommandReceived = time.time()
		self.deadManTimeout = 1 # second

	def safeRun(self):
		# receive new commands
		commands = None
		while self.conn.poll():
			commands = self.conn.recv()
			self.lastTimeCommandReceived = time.time()
		
		if commands == None:
			if time.time() - self.lastTimeCommandReceived > self.deadManTimeout:
				commands = PilotCommands() # dead man's switch activated -- stop the robot until you get another command
			else:
				time.sleep(.01)
		else: # command received
			self.lastTimeCommandReceived = time.time()

			ao = ArduinoOutputData()

			self.evalDriveCommand(ao, commands)
			self.evalRollerCommand(ao, commands)
			self.evalWinchCommand(ao, commands)
			self.evalRampCommand(ao, commands)

			ard.iolock.acquire()
			ard.otherConn.send(ao)
			ard.iolock.release()

	def cleanup(self):
		pass

	def evalDriveCommand(ao, commands):
		if commands.forwardSpeed == None:
			return

		if commands.desiredDeltaAngle != None: # pid control of angle (setting the turnSpeed command), then arcade drive on the result
			t = time.time()
			if lastPIDtime == None: # re-initialize PID
				p = 1
				i = .1
				d = 0
				iMax = 500
				iMin = -500
				uMax = 127  * 2 # at max should be sufficient to overcome any forward speed command
				uMin = -127 * 2
				self.pid = PID(p,i,d,iMax,iMin,uMax,uMin)
			else: # PID angle control
				commands.turnSpeed = pid.run(desiredDeltaAngle, t - self.lastPIDtime)

			lastPIDtime = t
		else:
			lastPIDtime = None

		if commands.turnSpeed != None: # turn based on turnSpeed(standard arcade drive)
			l = r = commands.forwardSpeed
			l += commands.turnSpeed
			r -= commands.turnSpeed
			tmp = max(abs(l), abs(r), 127)
			l = int(l*127/tmp)
			r = int(r*127/tmp)
			ard.leftSpeed = l
			ard.rightSpeed = r

	def evalRollerCommand(ao, commands):
		speedMap = {RollerCommands.STOP:0, RollerCommands.FORWARD:127, RollerCommands.REVERSE:-127}
		ao.rollerSpeed = speedMap[commands.rollerCommand]

	def evalWinchCommand(ao, commands):
		if commands.winchCommand == WinchCommands.UP:
			if not ai.topLimit:
				ao.winchSpeed = 127
			else:
				ao.winchSpeed = 0
		elif commands.winchCommand == WinchCommands.STOP:
			ao.winchSpeed = 0
		elif commands.winchCommand == WinchCommands.DOWN:
			if not ai.bottomLimit:
				ao.winchSpeed = -127
			else:
				ao.winchSpeed = 0
		elif commands.winchCommand == WinchCommands.HALF:
			raise NotImplementedError()

	def evalRampCommand(ao, commands):
		if commands.rampCommand == RampCommands.UP:
			ao.rampAngle = self.rampUpAngle
		elif commands.rampCommand == RampCommands.DOWN:
			ao.rampAngle = self.rampDownAngle
		elif commands.rampCommand == RampCommands.STOP:
			ao.rampAngle = self.lastRampCommand
		self.lastRampCommand = ao.rampAngle

