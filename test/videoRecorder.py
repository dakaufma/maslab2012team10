import cv2
import time

camera = cv2.VideoCapture(0)
vw = None
fpsFile = "fps"

fps = 30
try:
	f = open(fpsFile, "r")
	fps = int(float(f.read()))
	f.close()
	print fps
except:
	print "Failed to open fps file; using fps of 30"

try:
	cv2.namedWindow("feed")
	count = 0
	startTime = time.time()
	while True:
		count += 1
		f, img = camera.read()
		if vw==None:
			vw = cv2.VideoWriter("testVideo.avi", 0, fps, (img.shape[1], img.shape[0]))
		vw.write(img)
		cv2.imshow("feed", img)
		key = cv2.waitKey(1)
		if key == ord('q'):
			break
finally:
	camera.release()
	print count/(time.time()-startTime)
	f = open(fpsFile, "w")
	f.write("{0}\n".format(count/(time.time()-startTime)))
	f.close()


