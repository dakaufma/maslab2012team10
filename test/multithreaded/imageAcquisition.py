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
		
		self.fpsFile = "fps"

	def safeRun(self):
		self.logger.debug("Acquiring image")
		f,img = self.camera.read();

		if self.vw==None:
			self.vw = cv2.VideoWriter("logs/video.avi", 0, self.fps, (img.shape[1], img.shape[0]))
		self.vw.write(img)
		self.frameCount += 1

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

		self.fps = 30
		try:
			f = open(fpsFile, "r")
			self.fps = int(float(f.read()))
			f.close()
			print fps
		except:
			print "Failed to open fps file; using fps of 30"
		self.frameCount = 0
		self.startTime = systime.time()
		self.vw = None

	def cleanup(self):
		self.camera.release()
		f = open(self.fpsFile, "w")
		f.write("{0}\n".format(self.frameCount/(systime.time()-self.startTime)))
		f.close()
			
