#!/usr/bin/python

import imageAcquisition
import imageProcessing
import pilot
import control
import arduinoIO
import time as systime
import traceback
import subprocess

if __name__ == "__main__":
	ard = arduinoIO.ArduinoThread()
	ia = imageAcquisition.ImageAcquisitionThread(ard)
	ip = imageProcessing.ImageProcessingThread(ia)
	pi = pilot.Pilot(ard)
	behaviorManager = None

	threadList = [ard, ia, ip, pi]
	for stoppableThread in threadList:
		stoppableThread.start()
	try:
		# wait until there are readings for all arduino sensors
		print "Waiting for arduino sensor readings..."
		ard.lock.acquire()
		ai = ard.otherConn.recv() 
		ard.lock.release()

		# check to see if the battery is connected
		userWarning = None
		if not ai.robotPower:
			userWarning = "Hey! Power on the robot!"
		elif not ai.motorPower:
			userWarning = "Hey! Power on the motor controller!"
		if userWarning!=None:
			print userWarning
			try:
				subprocess.Popen(["espeak",userWarning])
			except:
				traceback.print_exc()

		# wait for falling edge on start button
		print "Waiting for falling edge..."
		pStart = False
		while not (pStart and not ai.startButton):
			pStart = ai.startButton

			if ard.lock.acquire(1):
				ai = ard.otherConn.recv()
				while ard.otherConn.poll():
					ai = ard.otherConn.recv()
				ard.lock.release()

				if pStart != ai.startButton:
					print "Start button changed to " + str(ai.startButton)
				systime.sleep(.01)

		# start control thread; wait 3 minutes and stop all threads
		behaviorManager = control.BehaviorManager(ard, pi, ip)
		print "Starting robot..."
		behaviorManager.start()
		systime.sleep(3*60 + 1)
	except:
		print "Error in runner??!?!??! That shouldn't happen...."
		traceback.print_exc()
		raise #do something else here?
	finally:
		print "Stopping robot..." # Note that the BehaviorManager should have already stopped it; this is a double check (plus it actually stops the threads).

		if behaviorManager!=None:
			behaviorManager.stopThread()
			behaviorManager.join()
		ard.lock.acquire() # send a command to stop all motors
		ard.otherConn.send(arduinoIO.ArduinoOutputData()) 
		ard.lock.release()
		systime.sleep(.1)

		for stoppableThread in threadList:
			stoppableThread.stopThread()
		for stoppableThread in threadList:
			stoppableThread.join()

		print "Done!"

