import threading

"""
This class implements a few extra features that we want all of our maslab threads to have.
	It can be stopped with a method call
	It automatically reinitializes and restarts the thread in case of an uncaught exception
	It provides a cleanup mechanism for closing communication channels, etc
This class should be overriden; in particular it has three methods that must be overriden.
"""
class StopableThread(threading.Thread):
	def __init__(self, obj):
		self.stop = threading.Event()
		self.obj = obj
        	threading.Thread.__init__(self)

	def stop(self):
		self.stop.set()

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
		while not self.stopped: # always loop unless you've been stopped
			try: # catches fatal exceptions so the thread can be restarted with its normal initialization
				self.safeInit()
				while not self.stopped(): # initialized; normal post-initialization loop
					safeRun() # sub-class runs stuff; if there is an exception it will be restarted
			except Exception as e:
				print self.name + " encountered a fatal error and will be restarted:"
				print "{0}: {1}".format(e.errno, e.strerror)

			finally:
				self.cleanup()
			
