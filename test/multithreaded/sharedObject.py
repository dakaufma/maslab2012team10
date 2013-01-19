import threading
import time as systime

class SharedObject:
	"""Safely shares an object between threads"""

	def __init__:
		self._lock = threading.Lock()
		self._obj = None
		self._time = None

	def get():
		self._lock.acquire()
		obj = self._obj
		time = self._time
		self._lock.release()
		return obj, time

	def set(obj, time=None):
		if time==None:
			time = systime.time()
		self._lock.acquire()
		self._obj = obj
		self._time = time
		self._lock.release()
