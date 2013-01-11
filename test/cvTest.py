#!/usr/bin/python

#intended to be run as `python ctTest.py ../reference_images/*`

import cv2.cv as cv
import sys
import math

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
	for row in range(0,distImg.rows):
		for col in range(0,distImg.cols):
			h = cv.Get2D(hue, row, col)[0]
			s = cv.Get2D(sat, row, col)[0]
			v = cv.Get2D(val, row, col)[0]
			cv.Set2D(distImg, row, col, (math.sqrt(
				(min(abs(h-colorHue),180-abs(h-colorHue))) ** 2 * hueWeight +
				(s-colorSat)                               ** 2 * satWeight +
				(v-colorVal)                               ** 2 * valWeight)
			))

def mouseListener(event, x, y, flags, img):
	if event==cv.CV_EVENT_LBUTTONDOWN:
		print "Click at (" + str(x) + ", " + str(y) + "):\tValue " + str(cv.Get2D(img, y, x))

def displayImage(windowName, img):
	cv.NamedWindow(windowName)
	cv.ShowImage(windowName, img)
	cv.SetMouseCallback(windowName, mouseListener, img)

if __name__ == '__main__':
	for fileName in sys.argv[1:]:
		#load image and shrink to a reasonable size
		img = cv.LoadImageM(fileName, cv.CV_LOAD_IMAGE_COLOR)
		smallImg = cv.CreateMat(img.rows/10, img.cols/10, cv.CV_8UC3)
		cv.Resize(img, smallImg)
		size = cv.GetSize(smallImg)

		#Display HSV channels
		hsv = cv.CreateMat(smallImg.rows, smallImg.cols, cv.CV_8UC3)
		hue = cv.CreateMat(smallImg.rows, smallImg.cols, cv.CV_8UC1)
		sat = cv.CreateMat(smallImg.rows, smallImg.cols, cv.CV_8UC1)
		val = cv.CreateMat(smallImg.rows, smallImg.cols, cv.CV_8UC1)
		cv.CvtColor(smallImg, hsv, cv.CV_BGR2HSV)
		cv.Split(hsv, hue, sat, val, None)

		#require that the hue is red
		redMask1 = cv.CreateMat(smallImg.rows, smallImg.cols, cv.CV_8UC1)
		redMask2 = cv.CreateMat(smallImg.rows, smallImg.cols, cv.CV_8UC1)
		redMask = cv.CreateMat(smallImg.rows, smallImg.cols, cv.CV_8UC1)
		cv.Threshold(hue, redMask1, redHueMax, 255, cv.CV_THRESH_BINARY_INV)
		cv.Threshold(hue, redMask2, redHueMin, 255, cv.CV_THRESH_BINARY)
		cv.Or(redMask1, redMask2, redMask)

		#Threshold for sufficiently small red distance
		#imperically determined 90 is a good threshold
		redDist = cv.CreateMat(smallImg.rows, smallImg.cols, cv.CV_8UC1)
		distFromColor(redDist, hue, sat, val, redHue, redSat, redVal, 1, 1, 1)

		redMaskedDist = cv.CreateMat(redDist.rows, redDist.cols, cv.CV_8UC1)
		cv.Set(redMaskedDist, 255)
		cv.Copy(redDist, redMaskedDist, redMask)

		#Combine masks for final red ball mask
		redImg = cv.CreateMat(redDist.rows, redDist.cols, cv.CV_8UC1)
		cv.Threshold(redMaskedDist, redImg, 90, 255, cv.CV_THRESH_BINARY_INV)
		displayImage("red", redImg)

		#Find blobs in red image
		storage = cv.CreateMemStorage()
		contour = cv.FindContours(redImg, storage)
		nextLargest = None
		nextArea = 0
		while contour:
			area = cv.ContourArea(contour)
			if area > 100: #minimum size imperically determined
				print area
				cv.DrawContours(smallImg, contour, cv.RGB(0,0,255), cv.RGB(0,0,255), 20)
			elif area>nextArea:
				nextArea = area
				nextLargest = contour
			contour = contour.h_next()
		if nextArea>0:
			print "Next largest: "+str(nextArea)
		print "-------------------------------"



		displayImage("ball detection", smallImg)
		displayImage("hue", hue)
		displayImage("sat", sat)
		displayImage("val", val)
		displayImage("red mask", redMask)
		displayImage("red dist", redDist)
		displayImage("red masked dist", redMaskedDist)
		key = cv.WaitKey()
		if key == 113:
			break
	cv.DestroyAllWindows()

