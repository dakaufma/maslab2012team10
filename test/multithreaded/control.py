from discretePID import PID 
from stoppableThread import StoppableThread
from arduinoIO import *
import time

class StateMachineThread(StoppableThread):
	"""Represents a state machine"""

	def __init__(self, initialState, arduinoConn, visionConn):
		super(StateMachineThread, self).__init__()
		self.initialState = initialState
		self.arduinoConn = arduinoConn
		self.visionConn = visionConn
		self.name = "StateMachine"

	def safeInit(self):
		self.state = self.initialState
		self.previousState = None
		self.lastVisionInput = None
		self.lastArduinoInput = None
		self.start = time.time()

	def safeRun(self):
		if (time.time()-self.start > 3*6):
			self.arduinoConn.send(ArduinoOutputData())
			return
		if self.previousState != self.state:
			print "Changed states: " + str(self.state)
		self.previousState = self.state

		while self.arduinoConn.poll():
			self.lastArduinoInput = self.arduinoConn.recv()
		while self.visionConn.poll():
			self.lastVisionInput = self.visionConn.recv()

		if self.state != None:
			self.state, output = self.state.execute(self.lastArduinoInput, self.lastVisionInput)
			self.arduinoConn.send(output)
		else:
			time.sleep(1)

	def cleanup(self):
		pass

class ControlState:
	"""Represents a single state of a state machine"""

	def execute(self, arduinoInput, visionInput):
		"""Executes the code for this state (should take very little time). Returns the next state to execute, which may be the same state object, and the arduino output"""
		raise NotImplementedError()

class Forward(ControlState):
	"""Goes forward. Can change states to track a ball or avoid a wall"""

	def __init__(self):
		self.forwardSpeed = 127
		self.minDist = 25 # cm

	def execute(self, arduinoInput, visionInput):
		output = ArduinoOutputData(self.forwardSpeed, self.forwardSpeed)
		state = self
		ai = arduinoInput
		vi = visionInput

		if ai.leftDist < self.minDist or ai.rightDist <= self.minDist:
			state = AvoidWall()
		elif vi != None and len(vi.balls) > 0:
			state = ApproachBall()

		return state, output

class AvoidWall(ControlState):
	def __init__(self):
		self.reverseSpeed = -127
		self.forwardSpeed = 40
		self.minDist = 25 # cm

	def execute(self, arduinoInput, visionInput):
		output = ArduinoOutputData()
		state = self
		ai = arduinoInput
		vi = visionInput

		if ai.leftDist < self.minDist and ai.leftDist <= ai.rightDist:
			output.rightSpeed = self.reverseSpeed
			output.leftSpeed = self.forwardSpeed
		elif ai.rightDist < self.minDist:
			output.leftSpeed = self.reverseSpeed
			output.rightSpeed = self.forwardSpeed
		else:
			state = Forward()
		
		return state, output

class ApproachBall(ControlState):
	def __init__(self):
		p = 1
		i = .1
		d = 0
		iMax = 500
		iMin = -500
		uMax = 127
		uMin = -127
		self.pid = PID(p,i,d,iMax,iMin,uMax,uMin)
		self.lastRunTime = None
		self.forwardSpeed = 80
		self.minDist = 25
		self.lastRunTime = None

	def execute(self, arduinoInput, visionInput):
		output = ArduinoOutputData(self.forwardSpeed, self.forwardSpeed)
		state = self
		ai = arduinoInput
		vi = visionInput

		if ai.leftDist < self.minDist or ai.rightDist <= self.minDist:
			state = AvoidWall()
		elif vi != None and len(vi.balls) == 0:
			state = Forward()
		else:
			t = time.time()
			if self.lastRunTime:
				closest = None
				for ball in vi.balls:
					if closest == None or ball.distance < closest.distance:
						closest = ball
				angle = closest.angle
				pidOut = int(pid.run(angle, t-self.lastRunTime))
				output.leftSpeed = approachSpeed + pidOut
				output.rightSpeed = approachSpeed - pidOut
				
				tmp = max(abs(output.leftSpeed), abs(output.rightSpeed), 127)
				output.leftSpeed = output.leftSpeed*127/tmp
				output.rightSpeed = output.rightSpeed*127/tmp
			lastRunTime = t
		return state, output

