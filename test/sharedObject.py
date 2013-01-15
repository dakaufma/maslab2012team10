# This class shares an obj between 2 threads in a thread-safe manner

import threading

class SharedObject:
	def __init__:
		self._lock = threading.Lock()
		self._obj = None
		self._time = None

	def getObject():
		self._lock.acquire()
		obj = self._obj
		time = self._time
		self._lock.release()
		return time, obj

	def setObject(obj, time):
		self._lock.acquire()
		self._obj = obj
		self._time = time
		self._lock.release()
