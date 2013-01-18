
# image processing thread

import cv2
import sys
import math
import numpy
import stoppableThread

redHue = 0
redHueMin = 170
redHueMax = 15
redSat = 255
redVal = 255

greenHue = 60
greenHueMin = 45
greenHueMax = 75
greenSat = 255
greenVal = 255

class ImageProcessingThread(StoppableThread):
	def distFromColor(self, distImg, maskedDistImg, mask, binImg, distThreshold, hue, sat, val, colorHue, colorSat, colorVal, hueWeight=1, satWeight=1, valWeight=1):
		if distImg  == None or distImg.shape != hue.shape:
			distImg = numpy.zeros(hue.shape, numpy.uint8)
		if maskedDistImg == None or maskedDistImg.shape!=hue.shape:
			maskedDistImg = numpy.zeros(hue.shape, numpy.uint8)
		if binImg == None or binImg.shape!=hue.shape:
			binImg = numpy.zeros(hue.shape, numpy.uint8)
		#distance = weighted average of dhue**2, dsat**2, dval**2
		scale = 1.0/(hueWeight + satWeight + valWeight)
		hueWeight *= scale
		satWeight *= scale
		valWeight *= scale
		hi = hue.item
		si = sat.item
		vi = val.item
		mi = mask.item
		di = distImg.itemset
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
		cv2.max(distImg, mask, maskedDistImg)
		cv2.threshold(maskedDistImg, distThreshold, 255, cv2.THRESH_BINARY_INV, binImg) 
		return distImg, maskedDistImg, binImg
				
	def getHSV(self, img, hsv=None, hue=None, sat=None, val=None):
		if hsv == None or hsv.shape!=img.shape:
			hsv = numpy.zeros(img.shape, numpy.uint8)
		if hue == None or hue.shape!=img.shape:
			hue = numpy.zeros(img.shape[:2], numpy.uint8)
		if sat == None or sat.shape!=img.shape:
			sat = numpy.zeros(img.shape[:2], numpy.uint8)
		if val == None or val.shape!=img.shape:
			val = numpy.zeros(img.shape[:2], numpy.uint8)
		cv2.cvtColor(img, cv2.COLOR_BGR2HSV, hsv)
		cv2.split(hsv, (hue, sat, val))
		return (hsv, hue, sat, val)

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

	def findBalls(self, img, hsv, hue, sat, val, colorDist, colorMaskedDist, colorImg, colorMask, colorMask1, colorMask2, distThreshold, minArea, colorHue, colorHueMin, colorHueMax, colorSat, colorVal, windowNamePrefix=""):
		#require that the hue is <color>; note that this mask has 0 for <color> pixels and 255 for non-<color>
		colorMask, colorMask1, colorMask2 = genColorMask(hue, colorHueMin, colorHueMax, colorMask, colorMask1, colorMask2);

		#Threshold for sufficiently small <color> distance
		colorDist, colorMaskedDist, colorImg = distFromColor(colorDist, colorMaskedDist, colorMask, colorImg, distThreshold, hue, sat, val, colorHue, colorSat, colorVal, 2, 1, 0);

		#Find blobs in <color> image
		contours, hierarchy = cv2.findContours(colorImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE);
		nextLargest = None
		nextArea = 0
		index = 0
		balls = []
		for contour in contours:
			area = cv2.contourArea(contour)
			if area > minArea:
				(x,y), radius = cv2.minEnclosingCircle(contour)
				angle = 78 * (x-img.shape[0]/2) / img.shape[0]
				print angle
				balls.append( (angle, x, y, radius, area, contour) )
			elif area>nextArea:
				nextArea = area
				nextLargest = index
			index += 1
		return colorDist, colorMaskedDist, colorImg, colorMask, colorMask1, colorMask2, balls

	def processImg(self, img, hsv, hue, sat, val, colorDist, colorMaskedDist, colorImg, colorMask, colorMask1, colorMask2, distThreshold, minArea):
		#get HSV channels
		hsv, hue, sat, val = getHSV(img, hsv, hue, sat, val);

		#find red balls
		redBalls = greenBalls = None
		colorDist, colorMaskedDist, colorImg, colorMask, colorMask1, colorMask2, redBalls = findBalls(img, hsv, hue, sat, val, colorDist, colorMaskedDist, colorImg, colorMask, colorMask1, colorMask2, distThreshold, minArea, redHue, redHueMin, redHueMax, redSat, redVal, "red")


		#find green balls
		colorDist, colorMaskedDist, colorImg, colorMask, colorMask1, colorMask2, greenBalls = findBalls(img, hsv, hue, sat, val, colorDist, colorMaskedDist, colorImg, colorMask, colorMask1, colorMask2, distThreshold, minArea, greenHue, greenHueMin, greenHueMax, greenSat, greenVal, "green")

		return hsv, hue, sat, val, colorDist, colorMaskedDist, colorImg, colorMask, colorMask1, colorMask2, redBalls, greenBalls


	def safe_init(self):
		self.camera = cv2.VideoCapture(1);
		self.hsv = self.hue = self.sat = self.val = self.redDist = self.redMaskedDist = self.redImg = self.redMask = self.redMask1 = self.redMask2 = None
		self.smallImg = None
		self.scale = .25
		self.distThreshold = 80 # empirically determined
		self.minArea = 25 # empirically determined

	def safe_run(self):
		while True:
			f,img = camera.read();
			if self.smallImg==None:
				self.smallImg = numpy.zeros((img.shape[0]*self.scale, img.shape[1]*self.scale, img.shape[2]), numpy.uint8)

			cv2.resize(img, None, self.smallImg, .25, .25)

			self.hsv, self.hue, self.sat, self.val, self.redDist, self.redMaskedDist, self.redImg, self.redMask, self.redMask1, self.redMask2, self.redBalls, self.greenBalls = self.processImg(self.smallImg, self.hsv, self.hue, self.sat, self.val, self.redDist, self.redMaskedDist, self.redImg, self.redMask, self.redMask1, self.redMask2, self.distThreshold, self.minArea, False)

			self.obj.setObject( (self.redBalls, self.greenBalls) )

	def cleanup(self):
		if self.camera and self.camera.isOpened():
			self.camera.release()

