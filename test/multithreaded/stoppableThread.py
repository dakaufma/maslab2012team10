import multiprocessing
import traceback
import time
import logging

"""
This class implements a few extra features that we want all of our processes to have.
	It provides an Event which can be used to stop the process cleanly
	It automatically reinitializes and restarts itself in case of an uncaught exception
	It provides a cleanup mechanism for closing communication channels, etc
Only subclasses of this class should be used; in particular safeInit(), safeRun(), and cleanup() throw exceptions if not overriden.
"""
class StoppableThread(multiprocessing.Process):
	def __init__(self, name=None):
		super(StoppableThread, self).__init__(name=name)
		self.stopSend, self.stopReceive = multiprocessing.Pipe()
		self.conn, self.otherConn = multiprocessing.Pipe()
		self.lock = multiprocessing.Lock()

		self.logger = logging.getLogger(self.name)
		handler = logging.FileHandler("logs/{0}".format(self.name))
		formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		handler.setFormatter(formatter)
		self.logger.addHandler(handler)
		self.logger.setLevel(logging.DEBUG)

	"""
	Stops the thread at the end of the next loop iteration
	"""
	def stopThread(self):
		self.stopSend.send(None)

	"""
	returns True if the thread has been commanded to stop
	"""
	def stopped(self):
		return self.stopReceive.poll()
	
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
		startTime = time.time()
		runCount = 0
		self.logger.info("Starting process")
		while not self.stopped(): # always loop unless you've been stopped
			try: # catches fatal exceptions so the thread can be restarted with its normal initialization
				self.logger.info("Initializing process")
				self.safeInit()
				self.logger.info("Normal process run state")
				while not self.stopped(): # initialized; normal post-initialization loop
					runCount += 1
					self.safeRun() # sub-class runs stuff; if there is an exception it will be restarted
			except KeyboardInterrupt:
				self.stopThread()
				self.logger.exception("Stopped by user")
				raise
			except Exception as e:
				print self.name + " encountered a fatal error and will be restarted:"
				traceback.print_exc()
				self.logger.exception("Fatal exception")

			finally:
				self.logger.info("Cleaning up")
				self.cleanup()
				duration = (time.time()-startTime)
				print "Thread " + self.name + " exiting with " + str(runCount) + " executions at " + str(runCount/duration) + " Hz"
				self.logger.info("Thread " + self.name + " exiting with " + str(runCount) + " executions at " + str(runCount/duration) + " Hz")

			time.sleep(2) # should only matter if threads consistently generate error messages
		self.conn.close()
		self.logger.info("Process done")
