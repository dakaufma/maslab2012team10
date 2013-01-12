Python 2.7.3 (default, Apr 10 2012, 23:31:26) [MSC v.1500 32 bit (Intel)] on win32
Type "copyright", "credits" or "license()" for more information.
>>> class PIDcontroller_discrete:
	def__init__(self, P=2.0, I=0.0, D=1.0, Derivator=0, Integrator=0,  Integrator_max=1500, Integrator_min=1000):
		
SyntaxError: invalid syntax
>>> def_init_(self, P=2.0, I=0.0, D=1.0, Derivator=0, Integrator=0,  Integrator_max=1500, Integrator_min=-1500)

Traceback (most recent call last):
  File "<pyshell#2>", line 1, in <module>
    def_init_(self, P=2.0, I=0.0, D=1.0, Derivator=0, Integrator=0,  Integrator_max=1500, Integrator_min=-1500)
NameError: name 'def_init_' is not defined
>>> def__init__(self, P=2.0, I=0.0, D=1.0, Derivator=0, Integrator=0,  Integrator_max=1500, Integrator_min=1000):
	
SyntaxError: invalid syntax
>>> ================================ RESTART ================================
>>> class PIDcontroller_discrete:
	def _init_(self, P=2.0, I=0.0, D=1.0, Derivator=0, Integrator=0,  Integrator_max=1500, Integrator_min=1000): #max and min are random values - need to be figured out empirically,filters?
		self.Kp=P
		self.Ki=I
		self.Kd=D
		self.Derivator=Derivator
		self.Integrator=Integrator
		self.Integrator_max=Integrator_max
		self.Integrator_min=Integrator_min
		self.desired_point=0.0
		self.error=0.0
	def update(self, current_value):
		self.error=self.desired_point - current_value
		self.P_value=self.Kp*self.error
		self.D_value=self.Kd*(self.error-self.Derivator)
		self.Derivator=self.error
		self.Integrator=self.Integrator+self.error
		if self.Integrator>self.Integrator_max:
			self.Integrator=self.Integrator_max
		elif self.Integrator<self.Integrator_min
		
SyntaxError: invalid syntax
>>> class PIDcontroller_discrete:
	def _init_(self, P=2.0, I=0.0, D=1.0, Derivator=0, Integrator=0,  Integrator_max=1500, Integrator_min=1000): #max and min are random values - need to be figured out empirically,filters?
		self.Kp=P
		self.Ki=I
		self.Kd=D
		self.Derivator=Derivator
		self.Integrator=Integrator
		self.Integrator_max=Integrator_max
		self.Integrator_min=Integrator_min
		self.desired_point=0.0
		self.error=0.0
	def update(self, current_value):
		self.error=self.desired_point - current_value
		self.P_value=self.Kp*self.error
		self.D_value=self.Kd*(self.error-self.Derivator)
		self.Derivator=self.error
		self.Integrator=self.Integrator+self.error
		if self.Integrator>self.Integrator_max:
			self.Integrator=self.Integrator_max
		elif self.Integrator<self.Integrator_min:
			self.Integrator=self.Integrator_min

			
>>> 		self.I_value=self.Integrator*self.Ki
		
  File "<pyshell#29>", line 1
    self.I_value=self.Integrator*self.Ki
   ^
IndentationError: unexpected indent
>>> class PIDcontroller_discrete:
	def _init_(self, P=2.0, I=0.0, D=1.0, Derivator=0, Integrator=0,  Integrator_max=1500, Integrator_min=1000): #max and min are random values - need to be figured out empirically,filters?
		self.Kp=P
		self.Ki=I
		self.Kd=D
		self.Derivator=Derivator
		self.Integrator=Integrator
		self.Integrator_max=Integrator_max
		self.Integrator_min=Integrator_min
		self.desired_point=0.0
		self.error=0.0
	def update(self, current_value):
		self.error=self.desired_point - current_value
		self.P_value=self.Kp*self.error
		self.D_value=self.Kd*(self.error-self.Derivator)
		self.Derivator=self.error
		self.Integrator=self.Integrator+self.error
		if self.Integrator>self.Integrator_max:
			self.Integrator=self.Integrator_max
		elif self.Integrator<self.Integrator_min:
			self.Integrator=self.Integrator_min
		self.I_value=self.Integrator*self.Ki
		PID=self.P_value+self.I_value+self.D_value
		return PID
	def desiredPoint(self, desired_point): #initialize desired point of PID
		self.desired_point=desired_point
		self.Integrator=0
		self.Derivator=0
	def setIntegrator(self, Integrator):
		self.Integrator=Integrator
	def setDerivator (self, Derivator):
		self.Derivator=Derivator
	def setKp(self, P):
		self.Kp=P
	def setKi(self, I):
		self.Ki=I
	def setKd(self, D):
		sefl.Kd=D
	def getPoint(self):
		return self.desired_point
	def getError(self):
		return self.error
	def getIntegrator(self):
		return self.Integrator
	def getDerivator(self):
		return self.Derivator
	
