
import cv2
import sys
import math
import numpy
import stoppableThread
import ball


class ImageProcessingThread(StoppableThread):
	"""Processes images to find red and green balls"""

	def __init__(self, imgObj):
	"""Instantiates the image processing thread using the provided SharedObject as a source of images"""
		self.imgObj = imgObj

	def safe_init(self):
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

	def safe_run(self):
		img, self.time = self.imgObj.get()
		if self.smallImg==None:
			self.smallImg = numpy.zeros((img.shape[0]*self.scale, img.shape[1]*self.scale, img.shape[2]), numpy.uint8)
		cv2.resize(img, None, self.smallImg, .25, .25)

		balls = processImg()
		self.obj.set(balls, self.time)

	def cleanup(self):
		pass

	def distFromColor(self, distThreshold, hue, sat, val, hueWeight=1, satWeight=1, valWeight=1):
		if self.distImg  == None or distImg.shape != self.hueImg.shape:
			self.distImg = numpy.zeros(self.hueImg.shape, numpy.uint8)
		if self.maskedDistImg == None or maskedDistImg.shape!=self.hueImg.shape:
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
		for row in xrange(0,distImg.shape[0]):
			for col in xrange(0,distImg.shape[1]):
				if mi(row, col) != 0:
					di((row, col), 255)
				else:
					h = hi(row, col) - colorHue
					s = si(row, col) - colorSat
					v = vi(row, col) - colorVal
					if h < -90:
						h+=180
					elif h > 90:
						h-=180
					di((row, col), math.sqrt(h*h*hueWeight + s*s*satWeight + v*v*valWeight))
		cv2.max(self.distImg, self.mask, self.maskedDistImg)
		cv2.threshold(self.maskedDistImg, self.distThreshold, 255, cv2.THRESH_BINARY_INV, self.binImg) 
				
	def getHSV(self):
		#create images if they don't already exist
		if self.hsvImg == None or self.hsv.shape != self.smallImg.shape:
			self.hsvImg = numpy.zeros(self.smallImg.shape, numpy.uint8)

		if self.hueImg == None or self.hueImg.shape != self.self.smallImg.shape:
			self.hueImg = numpy.zeros(self.smallImg.shape[:2], numpy.uint8)

		if self.satImg == None or self.satImg.shape != self.self.smallImg.shape:
			self.satImg = numpy.zeros(self.smallImg.shape[:2], numpy.uint8)

		if self.valImg == None or self.valImg.shape != self.self.smallImg.shape:
			self.valImg = numpy.zeros(self.smallImg.shape[:2], numpy.uint8)

		#convert from BGR to HSV
		cv2.cvtColor(self.smallImg, cv2.COLOR_BGR2HSV, self.hsvImg)
		cv2.split(self.hsvImg, (self.hueImg, self.satImg, self.valImg))

	def genColorMask(self, hue, colorHueMin, colorHueMax, colorMask=None, colorMask1=None, colorMask2=None):
		if colorMask1 == None or colorMask1.shape!=hue.shape:
			colorMask1 = numpy.zeros(hue.shape, numpy.uint8) 
		if colorMask2 == None or colorMask2.shape!=hue.shape:
			colorMask2 = numpy.zeros(hue.shape, numpy.uint8) 
		if colorMask == None or colorMask.shape!=hue.shape:
			colorMask  = numpy.zeros(hue.shape, numpy.uint8) 
		cv2.threshold(hue, colorHueMin, 255, cv2.THRESH_BINARY_INV, colorMask1)
		cv2.threshold(hue, colorHueMax, 255, cv2.THRESH_BINARY, colorMask2)
		if colorHueMin > colorHueMax: #hue wraps around; in this case we want the AND of the two masks
			cv2.min(colorMask1, colorMask2, colorMask)
		else: #min < max --> we want the OR of the two masks
			cv2.max(colorMask1, colorMask2, colorMask)
		return (colorMask, colorMask1, colorMask2)

	def findBalls(self, hue, hueMin, hueMax, sat, val):
		#require that the hue is <color>; note that this mask has 0 for <color> pixels and 255 for non-<color>
		getColorMask(hueMin, hueMax);

		#Threshold for sufficiently small generalized (color-based) distance
		distFromColor(distThreshold, hue, sat, val, 2, 1, 0);

		#Find blobs in <color> image
		contours, hierarchy = cv2.findContours(self.binImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE);
		nextLargest = None
		nextArea = 0
		index = 0
		balls = []
		for contour in contours:
			area = cv2.contourArea(contour)
			if area > minArea:
				(x,y), radius = cv2.minEnclosingCircle(contour)
				angle = 78 * (x-self.smallImg.shape[0]/2) / self.smallImg.shape[0]
				distance = 2.5 * (colorImage.shape[0] / (2*radius)) * (360/78.0) / (2*math.pi) 
				print angle
				balls.append( Ball(angle, None, time, distance) )
			elif area>nextArea:
				nextArea = area
				nextLargest = index
			index += 1

	def processImg(self):
		getHSV();

		balls = []

		#find red balls
		redBalls = findBalls(self.redHue, self.redHueMin, self.redHueMax, self.redSat, self.redVal)
		for ball in redBalls:
			ball.setRed(True)
			balls.append(ball)


		#find green balls
		greenBalls = findBalls(self.greenHue, self.greenHueMin, self.greenHueMax, self.greenSat, self.greenVal)
		for ball in greenBalls:
			ball.setRed(False)
			balls.append(ball)

		return balls


