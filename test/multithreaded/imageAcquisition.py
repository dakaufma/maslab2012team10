import cv2
import numpy
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

		self.scale = .25 # factor by which to scale down the acquired image
		
		self.fpsFile = "fps"

	def safeRun(self):
		self.logger.debug("Acquiring image")
		f,img = self.camera.read();

		# shink image for faster processing
		if self.smallImg==None:
			self.smallImg = numpy.zeros((img.shape[0]*self.scale, img.shape[1]*self.scale, img.shape[2]), numpy.uint8)
		cv2.resize(img, None, self.smallImg, self.scale, self.scale)

		if self.vw==None:
			self.logger.debug("Opening video file")
			self.vw = cv2.VideoWriter("logs/video.avi", 0, self.fps, (self.smallImg.shape[1], self.smallImg.shape[0]))
		self.logger.debug("Writing video frame")
		self.vw.write(self.smallImg)
		self.frameCount += 1

		self.logger.debug("Acquiring arudino lock")
		ai = None
		if self.ard.lock.acquire(1):
			while True:
				ai = self.ard.otherConn.recv() # note that you can't acquire images without receiving data from the arduino. Not ideal, but probably ok
				if not self.ard.otherConn.poll():
					break
			self.ard.lock.release()
		if ai != None:
			self.lastHeading = ai.heading
		heading = self.lastHeading

		self.conn.send( ImageData(self.smallImg, heading) )

	def safeInit(self):
		self.camera = cv2.VideoCapture(1)
		self.name = "ImageAcquisition"

		self.lastHeading = 0

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

		self.smallImg = None

	def cleanup(self):
		self.camera.release()
		f = open(self.fpsFile, "w")
		f.write("{0}\n".format(self.frameCount/(systime.time()-self.startTime)))
		f.close()
			
