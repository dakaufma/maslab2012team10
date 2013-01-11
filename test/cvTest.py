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

def distFromColor(distImg, hue, sat, val, colorHue, colorSat, colorVal, hueWeight=1, satWeight=1, valWeight=1):
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
			

def mouseListener(event, x, y, flags, img):
	if event==cv2.EVENT_LBUTTONDOWN:
		print "Click at (" + str(x) + ", " + str(y) + "):\tValue " + str(img[y, x])

def displayImage(windowName, img):
	cv2.namedWindow(windowName)
	cv2.imshow(windowName, img)
	cv2.setMouseCallback(windowName, mouseListener, img)

if __name__ == '__main__':
	for fileName in sys.argv[1:]:
		#load image and shrink to a reasonable size
		img = cv2.imread(fileName)
		smallImg = cv2.resize(img, None, None, .1, .1)

		#Display HSV channels
		hsv = numpy.zeros(smallImg.shape, numpy.uint8)
		hue = numpy.zeros(smallImg.shape[:2], numpy.uint8)
		sat = numpy.zeros(smallImg.shape[:2], numpy.uint8)
		val = numpy.zeros(smallImg.shape[:2], numpy.uint8)
		cv2.cvtColor(smallImg, cv2.COLOR_BGR2HSV, hsv)
		cv2.split(hsv, (hue, sat, val))

		#require that the hue is red; note that this mask has 0 for red pixels and 255 for non-red
		redMask1 = numpy.zeros(hue.shape, numpy.uint8) 
		redMask2 = numpy.zeros(hue.shape, numpy.uint8) 
		redMask  = numpy.zeros(hue.shape, numpy.uint8) 
		cv2.threshold(hue, redHueMin, 255, cv2.THRESH_BINARY_INV, redMask1)
		cv2.threshold(hue, redHueMax, 255, cv2.THRESH_BINARY, redMask2)
		if redHueMin > redHueMax: #hue wraps around; in this case we want the AND of the two masks
			cv2.min(redMask1, redMask2, redMask)
		else: #min < max --> we want the OR of the two masks
			cv2.max(redMask1, redMask2, redMask)

		#Threshold for sufficiently small red distance
		#imperically determined 90 is a good threshold
		redDist = numpy.zeros(hue.shape, numpy.uint8)
		distFromColor(redDist, hue, sat, val, redHue, redSat, redVal, 1, 1, 1)

		redMaskedDist = numpy.zeros(hue.shape, numpy.uint8)
		cv2.max(redDist, redMask, redMaskedDist)

		#Combine masks for final red ball mask
		redImg = numpy.zeros(redMask.shape, numpy.uint8)
		cv2.threshold(redMaskedDist, 90, 255, cv2.THRESH_BINARY_INV, redImg)
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

