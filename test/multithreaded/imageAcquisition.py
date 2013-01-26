import cv2
from stoppableThread import StoppableThread
import time as systime

class ImageData:
	"""Contains an image acquired by the camera and basic information about the image"""

	def __init__(self, img, heading, time=None):
		if time==None:
			time = systime.time()
		self.img = img
		self.heading = heading
		self.time = time

class ImageAcquisitionThread(StoppableThread):
	"""Thread that acquires images from a camera"""

	def __init__(self, ard):
		super(ImageAcquisitionThread, self).__init__(name="ImageAcquisition")
		self.ard = ard

	def safeRun(self):
		self.logger.debug("Acquiring image")
		f,img = self.camera.read();

		self.logger.debug("Acquiring arudino lock")
		self.ard.lock.acquire()
		ai = None
		while True:
			ai = self.ard.otherConn.recv() # note that you can't acquire images without receiving data from the arduino. Not ideal, but probably ok
			if not self.ard.otherConn.poll():
				break
		self.ard.lock.release()
		heading = 0 if ai==None else ai.heading

		self.conn.send( ImageData(img, heading) )

	def safeInit(self):
		self.camera = cv2.VideoCapture(0)
		self.name = "ImageAcquisition"

	def cleanup(self):
		self.camera.release()
			
