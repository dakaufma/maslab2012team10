#!/usr/bin/python

#intended to be run as `python ctTest.py ../reference_images/*`

import cv2
import sys
import math
import numpy

redHue = 0
redSat = 255
redVal = 255
redHueMax = 15
redHueMin = 170

def distFromColor(distImg, maskedDistImg, mask, binImg, hue, sat, val, colorHue, colorSat, colorVal, hueWeight=1, satWeight=1, valWeight=1):
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
	for row in xrange(0,distImg.shape[0]):
		for col in xrange(0,distImg.shape[1]):
			h = hi(row, col) - colorHue
			s = si(row, col) - colorSat
			v = vi(row, col) - colorVal
			if h < -90:
				h+=180
			elif h > 90:
				h-=180
			distImg.itemset((row, col), math.sqrt(h*h*hueWeight + s*s*satWeight + v*v*valWeight))
	cv2.max(distImg, mask, maskedDistImg)
	cv2.threshold(maskedDistImg, 90, 255, cv2.THRESH_BINARY_INV, binImg) #imperically determined 90 is a good threshold
	return distImg, maskedDistImg, binImg
			

def mouseListener(event, x, y, flags, img):
	if event==cv2.EVENT_LBUTTONDOWN:
		print "Click at (" + str(x) + ", " + str(y) + "):\tValue " + str(img[y, x])

def displayImage(windowName, img):
	cv2.namedWindow(windowName)
	cv2.imshow(windowName, img)
	cv2.setMouseCallback(windowName, mouseListener, img)

def getHSV(img, hsv=None, hue=None, sat=None, val=None):
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

def genRedMask(hue, redMask=None, redMask1=None, redMask2=None):
	if redMask1 == None or redMask1.shape!=hue.shape:
		redMask1 = numpy.zeros(hue.shape, numpy.uint8) 
	if redMask2 == None or redMask2.shape!=hue.shape:
		redMask2 = numpy.zeros(hue.shape, numpy.uint8) 
	if redMask == None or redMask.shape!=hue.shape:
		redMask  = numpy.zeros(hue.shape, numpy.uint8) 
	cv2.threshold(hue, redHueMin, 255, cv2.THRESH_BINARY_INV, redMask1)
	cv2.threshold(hue, redHueMax, 255, cv2.THRESH_BINARY, redMask2)
	if redHueMin > redHueMax: #hue wraps around; in this case we want the AND of the two masks
		cv2.min(redMask1, redMask2, redMask)
	else: #min < max --> we want the OR of the two masks
		cv2.max(redMask1, redMask2, redMask)
	return (redMask, redMask1, redMask2)

if __name__ == '__main__':
	for fileName in sys.argv[1:]:
		#load image and shrink to a reasonable size
		img = cv2.imread(fileName)
		smallImg = cv2.resize(img, None, None, .1, .1)

		#Display HSV channels
		hsv = hue = sat = val = None 
		hsv, hue, sat, val = getHSV(smallImg, hsv, hue, sat, val)

		#require that the hue is red; note that this mask has 0 for red pixels and 255 for non-red
		redMask = redMask1 = redMask2  = None
		redMask, redMask1, redMask2 = genRedMask(hue, redMask, redMask1, redMask2)

		#Threshold for sufficiently small red distance
		redDist = redMaskedDist = redImg = None
		redDist, redMaskedDist, redImg = distFromColor(redDist,redMaskedDist, redMask, redImg, hue, sat, val, redHue, redSat, redVal, 1, 1, 1)
		displayImage("red", redImg)

		#Find blobs in red image
		contours, hierarchy = cv2.findContours(redImg, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
		nextLargest = None
		nextArea = 0
		index = 0
		for contour in contours:
			area = cv2.contourArea(contour)
			if area > 100: #minimum area imperically determined
				print area
				(x,y), radius = cv2.minEnclosingCircle(contour)
				cv2.circle(smallImg,(int(x),int(y)), int(radius), (255,0,0), 3)
				#cv2.drawContours(smallImg, contours, index, (255,0,0), 3)
			elif area>nextArea:
				nextArea = area
				nextLargest = index
			index += 1
		if nextArea>0:
			print "Next largest: "+str(nextArea)
			cv2.drawContours(smallImg, contours, nextLargest, (0,255,0), 3)
		print "-------------------------------"



		displayImage("ball detection", smallImg)
		displayImage("hue", hue)
		displayImage("sat", sat)
		displayImage("val", val)
		displayImage("red mask", redMask)
		displayImage("red dist", redDist)
		displayImage("red masked dist", redMaskedDist)
		key = cv2.waitKey()
		if key == 113:
			break
	cv2.destroyAllWindows()

