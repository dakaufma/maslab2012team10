import cv2
import stoppableThread.StoppableThread

class imageAcquisitionThread(StoppableThread):
	"""Thread that acquires images from a camera"""

	def safeRun(self):
		f,img = self.camera.read();
		self.obj.setObject(img)

	def safeInit(self):
		self.camera = cv2.VideoCapture(1)

	def cleanup(self):
		camera.release()
			
