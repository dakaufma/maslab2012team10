import cv2
import time
import threading
class imageA(threading.Thread):
	def __init__(self, obj):
        	threading.Thread.__init__(self)
		self._stop = threading.Event()
		self._obj = obj

	def stop(self):
		self._stop.set()

	def stopped(self):
		return self._stop.isSet()

	def run(self):
		while not stopped:
			#read images from the camera
			try:
				camera = cv2.VideoCapture(1);
				while not stopped:
					try:
						f,img = camera.read();
						obj.setObject(obj)
					except(KeyboardInterrupt):
						stopped.self()
						print "Image acquision thread exiting on keyoard interupt"
					except:
						break
			except:
				print "GAH! I'm blind!"
			finally:
				camera.release()
			
