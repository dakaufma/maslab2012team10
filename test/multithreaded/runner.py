#!/usr/bin/python

import imageAcquisition
import imageProcessing
import control
import arduinoIO
import time as systime

if __name__ == "__main__":
	ard = arduinoIO.ArduinoThread()
	ia = imageAcquisition.ImageAcquisitionThread(ard)
	ip = imageProcessing.ImageProcessingThread(ia)
	stateMachine = None

	threadList = [ard, ia, ip]
	for stoppableThread in threadList:
		stoppableThread.start()
	try:
		# wait until there are readings for all arduino sensors
		print "Waiting for arduino sensor readings..."
		ard.lock.acquire()
		ai = ard.otherConn.recv() 
		ard.lock.release()

		# wait for falling edge on start button
		print "Waiting for falling edge..."
		pStart = False
		while not (pStart and not ai.startButton):
			pStart = ai.startButton

			ard.lock.acquire()
			ai = ard.otherConn.recv()
			while ard.otherConn.poll():
				ai = ard.otherConn.recv()
			ard.lock.release()

			if pStart != ai.startButton:
				print "Start button changed to " + str(ai.startButton)
			systime.sleep(.01)

		# start control thread; wait 3 minutes and stop all threads
		stateMachine = control.StateMachineThread(ard, ip)
		print "Starting robot..."
		stateMachine.start()
		systime.sleep(3*60)
	except:
		raise #do something else here?
	finally:
		print "Stopping robot..."

		if stateMachine!=None:
			stateMachine.stopThread()
			stateMachine.join()
		ard.lock.acquire() # send a command to stop all motors
		ard.otherConn.send(arduinoIO.ArduinoOutputData()) 
		ard.lock.release()
		systime.sleep(.1)

		for stoppableThread in threadList:
			stoppableThread.stopThread()
		for stoppableThread in threadList:
			stoppableThread.join()

		print "Done!"

