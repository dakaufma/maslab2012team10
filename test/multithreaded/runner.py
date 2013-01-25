import imageAcquisition
import imageProcessing
import control
import arduinoIO
import time as systime

if __name__ == "__main__":
	ard = arduinoIO.ArduinoThread()
	ardConn = ard.otherConn
	ia = imageAcquisition.ImageAcquisitionThread()
	ip = imageProcessing.ImageProcessingThread(ia.otherConn)
	ipConn = ip.otherConn

	threadList = [ard, ia, ip]
	for stoppableThread in threadList:
		stoppableThread.start()
	try:
		# wait until there are readings for all arduino sensors
		print "Waiting for arduino sensor readings..."
		ai = ardConn.recv() 

		# wait for falling edge on start button
		print "Waiting for falling edge..."
		pStart = False
		while not (pStart and not ai.startButton):
			pStart = ai.startButton
			ai = ardConn.recv()
			while ardConn.poll():
				ai = ardConn.recv()
			if pStart != ai.startButton:
				print "Start button changed to " + str(ai.startButton)
			systime.sleep(.01)

		# start control thread; wait 3 minutes and stop all threads
		stateMachine = control.StateMachineThread(control.Forward(), ardConn, ipConn)
		print "Starting robot..."
		stateMachine.start()
		systime.sleep(3*60)
	except:
		raise #do something else here?
	finally:
		print "Stopping robot..."

		stateMachine.stopThread()
		stateMachine.join()
		ardConn.send(arduinoIO.ArduinoOutputData()) # send a command to stop all motors
		systime.sleep(.1)

		for stoppableThread in threadList:
			stoppableThread.stopThread()
		for stoppableThread in threadList:
			stoppableThread.join()

		print "Done!"

