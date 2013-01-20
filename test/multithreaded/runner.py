import imageAcquisition
import imageProcessing
import control
import arduinoIO
import time as systime

if __name__ == "__main__":
	ard = arduinoIO.ArduinoThread()
	ia = imageAcquisition.ImageAcquisitionThread()
	ip = imageProcessing.ImageProcessingThread(ia.obj)
	threadList = [ard, ia, ip]
	for stoppableThread in threadList:
		stoppableThread.start()

	stateMachine = control.StateMachineThread(control.Forward(), ard.inputObj, ip.obj, ard.outputObj)
	threadList.append(stateMachine)

	# wait until there are readings for all arduino sensors
	print "Waiting for arduino sensor readings..."
	ai, time = ard.inputObj.get()
	while ai.leftDist == None or ai.rightDist == None or ai.startButton == None:
		ai, time = ard.inputObj.get()
		systime.sleep(.01)

	# wait for falling edge on start button
	print "Waiting for rising edge..."
	pStart = False
	while not (pStart and not ai.startButton):
		pStart = ai.startButton
		ai, time = ard.inputObj.get()
		systime.sleep(.01)

	# start control thread; wait 3 minutes and stop all threads
	print "Starting robot..."
	stateMachine.start()
	systime.sleep(3*6)

	print "Stopping robot..."
	for stoppableThread in threadList:
		stoppableThread.stopThread()
	for stoppableThread in threadList:
		stoppableThread.join()

	print "Done! Hell yeah!"

