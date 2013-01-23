from arduinoIO import *


at = ArduinoThread()
print "Starting"
at.start()
print "Started"
pAtWall = False
try:
	while True:
		ai, time = at.inputObj.get()
		if ai == None or ai.leftDist == None:
			continue
		atWall = ai.leftDist < 20 or ai.rightDist < 20
		if atWall != pAtWall:
			print atWall
		pAtWall = atWall
except:
	print "Stopping"
	at.stopThread()
	at.join()
	raise
print "Done"
