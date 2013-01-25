import cv2
import sys
import math
import numpy
import time
from stoppableThread import StoppableThread
import ball

class ImageData:
	"""Data structure containing all information derived from vision"""
	def __init__(self, imgTime, balls=None):
		self.imgTime = imgTime
		self.balls = balls

class ImageProcessingThread(StoppableThread):
	"""Processes images to find red and green balls"""

	def __init__(self, imgConn):
		"""Instantiates the image processing thread using the provided SharedObject as a source of images"""
		super(ImageProcessingThread, self).__init__()
		self.imgConn = imgConn
		self.name = "ImageProcessing"

	def safeInit(self):
		self.smallImg = None # smaller version of the acquired image
		self.hsvImg = None # image stored in hsv
		self.hueImg = None # hue component
		self.satImg = None # saturation component
		self.valImg = None # value component
		self.distImg = None # generalized distance from pixel color to a specific color
		self.mask = None # hue-based mask of the image
		self.mask1 = None # image used to create the mask
		self.mask2 = None # other image used to create the mask
		self.maskedDistImg = None # distImg masked by the mask
		self.binImg = None # binary image (get ball contours from this)

		self.scale = .25 # factor by which to scale down the acquired image
		self.distThreshold = 80 # empirically determined
		self.minArea = 25 # empirically determined
		self.time = None # the time the image was acquired; taken from the SharedObject

		self.redHue = 0
		self.redHueMin = 170
		self.redHueMax = 15
		self.redSat = 255
		self.redVal = 255

		self.greenHue = 60
		self.greenHueMin = 45
		self.greenHueMax = 75
		self.greenSat = 255
		self.greenVal = 255

	def safeRun(self):
		img = None
		while self.imgConn.poll():
			img, self.imgTime = self.imgConn.recv()
		if img == None:
			time.sleep(.01)
			return
		if self.smallImg==None:
			self.smallImg = numpy.zeros((img.shape[0]*self.scale, img.shape[1]*self.scale, img.shape[2]), numpy.uint8)
		cv2.resize(img, None, self.smallImg, .25, .25)

		balls = self.processImg()
		self.conn.send(ImageData(self.imgTime, balls))

	def cleanup(self):
		pass

	def distFromColor(self, distThreshold, hue, sat, val, hueWeight=1, satWeight=1, valWeight=1):
		if self.distImg  == None or self.distImg.shape != self.hueImg.shape:
			self.distImg = numpy.zeros(self.hueImg.shape, numpy.uint8)
		if self.maskedDistImg == None or self.maskedDistImg.shape!=self.hueImg.shape:
			self.maskedDistImg = numpy.zeros(self.hueImg.shape, numpy.uint8)
		if self.binImg == None or self.binImg.shape!=self.hueImg.shape:
			self.binImg = numpy.zeros(self.hueImg.shape, numpy.uint8)
		#distance = weighted average of dhue**2, dsat**2, dval**2
		scale = 1.0/(hueWeight + satWeight + valWeight)
		hueWeight *= scale
		satWeight *= scale
		valWeight *= scale
		hi = self.hueImg.item
		si = self.satImg.item
		vi = self.valImg.item
		mi = self.mask.item
		di = self.distImg.itemset
		for row in xrange(0,self.distImg.shape[0]):
			for col in xrange(0,self.distImg.shape[1]):
				if mi(row, col) != 0:
					di((row, col), 255)
				else:
					h = hi(row, col) - hue
					s = si(row, col) - sat
					v = vi(row, col) - val
					if h < -90:
						h+=180
					elif h > 90:
						h-=180
					di((row, col), math.sqrt(h*h*hueWeight + s*s*satWeight + v*v*valWeight))
		cv2.max(self.distImg, self.mask, self.maskedDistImg)
		cv2.threshold(self.maskedDistImg, self.distThreshold, 255, cv2.THRESH_BINARY_INV, self.binImg) 
				
	def getHSV(self):
		#create images if they don't already exist
		if self.hsvImg == None or self.hsvImg.shape != self.smallImg.shape:
			self.hsvImg = numpy.zeros(self.smallImg.shape, numpy.uint8)

		if self.hueImg == None or self.hueImg.shape != self.smallImg.shape:
			self.hueImg = numpy.zeros(self.smallImg.shape[:2], numpy.uint8)

		if self.satImg == None or self.satImg.shape != self.smallImg.shape:
			self.satImg = numpy.zeros(self.smallImg.shape[:2], numpy.uint8)

		if self.valImg == None or self.valImg.shape != self.smallImg.shape:
			self.valImg = numpy.zeros(self.smallImg.shape[:2], numpy.uint8)

		#convert from BGR to HSV
		cv2.cvtColor(self.smallImg, cv2.COLOR_BGR2HSV, self.hsvImg)
		cv2.split(self.hsvImg, (self.hueImg, self.satImg, self.valImg))

	def getColorMask(self, colorHueMin, colorHueMax):
		if self.mask1 == None or self.mask1.shape!=self.hueImg.shape:
			self.mask1 = numpy.zeros(self.hueImg.shape, numpy.uint8) 
		if self.mask2 == None or self.mask2.shape!=self.hueImg.shape:
			self.mask2 = numpy.zeros(self.hueImg.shape, numpy.uint8) 
		if self.mask == None or self.mask.shape!=self.hueImg.shape:
			self.mask  = numpy.zeros(self.hueImg.shape, numpy.uint8) 
		cv2.threshold(self.hueImg, colorHueMin, 255, cv2.THRESH_BINARY_INV, self.mask1)
		cv2.threshold(self.hueImg, colorHueMax, 255, cv2.THRESH_BINARY, self.mask2)
		if colorHueMin > colorHueMax: #hueImg wraps around; in this case we want the AND of the two masks
			cv2.min(self.mask1, self.mask2, self.mask)
		else: #min < max --> we want the OR of the two masks
			cv2.max(self.mask1, self.mask2, self.mask)

	def findBalls(self, hue, hueMin, hueMax, sat, val):
		#require that the hue is <color>; note that this mask has 0 for <color> pixels and 255 for non-<color>
		self.getColorMask(hueMin, hueMax);

		#Threshold for sufficiently small generalized (color-based) distance
		self.distFromColor(self.distThreshold, hue, sat, val, 2, 1, 0);

		#Find blobs in <color> image
		contours, hierarchy = cv2.findContours(self.binImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE);
		nextLargest = None
		nextArea = 0
		index = 0
		balls = []
		for contour in contours:
			area = cv2.contourArea(contour)
			if area > self.minArea:
				(x,y), radius = cv2.minEnclosingCircle(contour)
				angle = 78 * (x-self.smallImg.shape[0]/2) / self.smallImg.shape[0]
				distance = 2.5 * (self.binImg.shape[0] / (2*radius)) * (360/78.0) / (2*math.pi) 
				#print angle
				balls.append( ball.Ball(angle, None, self.imgTime, distance) )
			elif area>nextArea:
				nextArea = area
				nextLargest = index
			index += 1
		return balls

	def processImg(self):
		self.getHSV();

		balls = []

		#find red balls
		redBalls = self.findBalls(self.redHue, self.redHueMin, self.redHueMax, self.redSat, self.redVal)
		for ball in redBalls:
			ball.setRed(True)
			balls.append(ball)


		#find green balls
		greenBalls = self.findBalls(self.greenHue, self.greenHueMin, self.greenHueMax, self.greenSat, self.greenVal)
		for ball in greenBalls:
			ball.setRed(False)
			balls.append(ball)

		return balls


