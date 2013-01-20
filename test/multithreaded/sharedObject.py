import threading
import time as systime

class SharedObject:
	"""Safely shares an object between threads"""

	def __init__(self):
		self.lock = threading.Lock()
		self.obj = None
		self.time = None

	def get(self):
		self.lock.acquire()
		obj = self.obj
		time = self.time
		self.lock.release()
		return obj, time

	def set(self, obj, time=None):
		if time==None:
			time = systime.time()
		self.lock.acquire()
		self.obj = obj
		self.time = time
		self.lock.release()
