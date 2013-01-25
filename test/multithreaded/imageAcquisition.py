import cv2
from stoppableThread import StoppableThread
import time

class ImageAcquisitionThread(StoppableThread):
	"""Thread that acquires images from a camera"""

	def init(self):
		super(ImageAcquisitionThread, self).__init__()
		self.name = "ImageAcquisition"

	def safeRun(self):
		f,img = self.camera.read();
		self.conn.send( (img, time.time()) )

	def safeInit(self):
		self.camera = cv2.VideoCapture(2)
		self.name = "ImageAcquisition"

	def cleanup(self):
		self.camera.release()
			
