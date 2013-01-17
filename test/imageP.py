#!/usr/bin/python

#uses ball detection from cvTest and PID control to drive the robot towards balls

from cvTest import processImg
from discretePID import PID
import cv2
import numpy
import sys
sys.path.append("..")
import time
import arduino

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


MIN_DIST = 15 #cm

if __name__ == '__main__':

	try:
		hsv = hue = sat = val = redDist = redMaskedDist = redImg = redMask = redMask1 = redMask2 = None
		smallImg = None
		scale = .25
		distThreshold = 80 # empirically determined
		minArea = 25 # empirically determined

				if smallImg==None:
					smallImg = numpy.zeros((img.shape[0]*scale, img.shape[1]*scale, img.shape[2]), numpy.uint8)

				cv2.resize(img, None, smallImg, .25, .25)

				hsv, hue, sat, val, redDist, redMaskedDist, redImg, redMask, redMask1, redMask2, redBalls, greenBalls = processImg(smallImg, hsv, hue, sat, val, redDist, redMaskedDist, redImg, redMask, redMask1, redMask2, distThreshold, minArea)
