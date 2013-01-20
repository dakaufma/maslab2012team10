import cv2
from stoppableThread import StoppableThread

class ImageAcquisitionThread(StoppableThread):
	"""Thread that acquires images from a camera"""

	def init(self):
		super(ImageAcquisitionThread, self).__init__()
		self.name = "ImageAcquisition"

	def safeRun(self):
		f,img = self.camera.read();
		self.obj.set(img)

	def safeInit(self):
		self.camera = cv2.VideoCapture(1)

	def cleanup(self):
		self.camera.release()
			
