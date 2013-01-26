from discretePID import PID 
from stoppableThread import StoppableThread
from arduinoIO import *
import time

class StateMachineThread(StoppableThread):
	"""Represents a state machine"""

	def __init__(self, ard, vision):
		super(StateMachineThread, self).__init__("StateMachine")
		self.initialState = Forward(self.logger)
		self.ard = ard
		self.vision = vision

	def safeInit(self):
		self.state = self.initialState
		self.previousState = None
		self.lastVisionInput = None
		self.lastArduinoInput = None
		self.start = time.time()

	def safeRun(self):
		# stop the robot if time has elapsed
		if (time.time()-self.start > 3*60):
			self.ard.lock.acquire()
			self.ard.otherConn.send(ArduinoOutputData())
			self.ard.lock.release()
			return
		
		# print state changes
		if self.previousState != self.state:
			print "Changed states: " + str(self.state)
			self.logger.info("Changed states: " + str(self.state))
		self.previousState = self.state

		self.ard.lock.acquire()
		while self.ard.otherConn.poll():
			self.lastArduinoInput = self.ard.otherConn.recv()
		self.ard.lock.release()
		self.vision.lock.acquire()
		while self.vision.conn.poll():
			self.lastVisionInput = self.vision.otherConn.recv()
		self.vision.lock.release()

		if self.state != None:
			self.state, output = self.state.execute(self.lastArduinoInput, self.lastVisionInput)
			self.ard.lock.acquire()
			self.ard.otherConn.send(output)
			self.ard.lock.release()
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

	def __init__(self, logger):
		self.forwardSpeed = 127
		self.minDist = 25 # cm
		self.logger = logger

	def execute(self, arduinoInput, visionInput):
		output = ArduinoOutputData(self.forwardSpeed, self.forwardSpeed)
		state = self
		ai = arduinoInput
		vi = visionInput

		if ai.leftDist < self.minDist or ai.rightDist <= self.minDist:
			state = AvoidWall(self.logger)
		elif vi != None and len(vi.balls) > 0:
			state = ApproachBall(self.logger)

		return state, output

class AvoidWall(ControlState):
	def __init__(self, logger):
		self.reverseSpeed = -127
		self.forwardSpeed = 40
		self.minDist = 25 # cm
		self.logger = logger

	def execute(self, arduinoInput, visionInput):
		output = ArduinoOutputData()
		state = self
		ai = arduinoInput
		vi = visionInput

		if ai.leftDist < self.minDist and ai.leftDist <= ai.rightDist:
			output.rightSpeed = self.reverseSpeed
			output.leftSpeed = self.forwardSpeed
			self.logger.debug("Avoiding wall on the left")
		elif ai.rightDist < self.minDist:
			output.leftSpeed = self.reverseSpeed
			output.rightSpeed = self.forwardSpeed
			self.logger.debug("Avoiding wall on the right")
		else:
			state = Forward(self.logger)
		
		return state, output

class ApproachBall(ControlState):
	def __init__(self, logger):
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
		self.logger = logger

	def execute(self, arduinoInput, visionInput):
		output = ArduinoOutputData(self.forwardSpeed, self.forwardSpeed)
		state = self
		ai = arduinoInput
		vi = visionInput

		if ai.leftDist < self.minDist or ai.rightDist <= self.minDist:
			state = AvoidWall(self.logger)
		elif vi != None and len(vi.balls) == 0:
			state = Forward(self.logger)
		else:
			t = time.time()
			if self.lastRunTime:
				closest = None
				for ball in vi.balls:
					if closest == None or ball.distance < closest.distance:
						closest = ball
				angle = closest.angle
				self.logger.debug("Approaching ball at {0} degrees, {1} cm".format(closest.angle, closest.distance))
				pidOut = int(pid.run(angle, t-self.lastRunTime))
				output.leftSpeed = approachSpeed + pidOut
				output.rightSpeed = approachSpeed - pidOut
				
				tmp = max(abs(output.leftSpeed), abs(output.rightSpeed), 127)
				output.leftSpeed = output.leftSpeed*127/tmp
				output.rightSpeed = output.rightSpeed*127/tmp
			lastRunTime = t
		return state, output

