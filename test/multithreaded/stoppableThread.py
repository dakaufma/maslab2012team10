import threading
import traceback
import time
from sharedObject import SharedObject

"""
This class implements a few extra features that we want all of our maslab threads to have.
	It can be stopped with a method call
	It automatically reinitializes and restarts the thread in case of an uncaught exception
	It provides a cleanup mechanism for closing communication channels, etc
This class should be overriden; in particular it has three methods that must be overriden.
"""
class StoppableThread(threading.Thread):
	def __init__(self):
		super(StoppableThread, self).__init__()
		self.stop = threading.Event()
		self.obj = SharedObject()

	"""
	Stops the thread at the end of the next loop iteration
	"""
	def stopThread(self):
		self.stop.set()

	"""
	returns True if the thread has been commanded to stop
	"""
	def stopped(self):
		return self.stop.isSet()
	
	"""
	normal thread activities; to be implemented by the subclass
	"""
	def safeRun(self):
		raise NotImplementedError 

	"""
	potentially error-throwing initialization; to be implemented by the subclass
	"""
	def safeInit(self):
		raise NotImplementedError  

	"""
	to be implemented by a subclass
	"""
	def cleanup(self):
		raise NotImplementedError  

	def run(self):
		while not self.stopped(): # always loop unless you've been stopped
			try: # catches fatal exceptions so the thread can be restarted with its normal initialization
				self.safeInit()
				while not self.stopped(): # initialized; normal post-initialization loop
					self.safeRun() # sub-class runs stuff; if there is an exception it will be restarted
			except KeyboardInterrupt:
				self.stop()
				raise
			except Exception as e:
				print self.name + " encountered a fatal error and will be restarted:"
				traceback.print_exc()

			finally:
				self.cleanup()
			time.sleep(2) # should only matter if threads consistently generate error messages
			
