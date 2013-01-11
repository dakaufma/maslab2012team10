import cv2.cv as cv

hscale = 3
height = 50

def mouseListener(event, x, y, flags, img):
	if event==cv.CV_EVENT_LBUTTONDOWN:
		print str(x/hscale % 180)

def displayImage(windowName, img):
	cv.NamedWindow(windowName)
	cv.ShowImage(windowName, img)
	cv.SetMouseCallback(windowName, mouseListener, img)

if __name__=="__main__":
	img = cv.CreateMat(height, 180*hscale * 2, cv.CV_8UC3)
	rgb = cv.CreateMat(height, 180*hscale * 2, cv.CV_8UC3)
	for col in range(0,img.cols):
		for row in range(0, img.rows):
			cv.Set2D(img, row, col, (col / hscale % 180,255,255))
	cv.CvtColor(img, rgb, cv.CV_HSV2BGR)
	displayImage("hsv", rgb)
	cv.WaitKey()
	cv.DestroyAllWindows()


