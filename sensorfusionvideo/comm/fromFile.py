####################################################
# Read sensor data from file
#
# Arasch Lagies
# Version: 3/19/2020
# Last update:
#
####################################################
import os
import time

FILEPATH = "data/"
FILENAME = "accelerometer_sample_data.txt"
BASIS    = 16

class Comm():
	def __init__(self, path= FILEPATH, sensor=FILENAME, basis=BASIS, test=False):
		self.running = True					# Flag to run and terminate while loop
		self.basis   = basis
		self.test    = test
		self.sensor  = os.path.join(path, sensor)
		
		
	def readLoop(self, q):
		value = 0
		while(self.running):
			with open(self.sensor, 'r') as f:
				for l in f:
					l = l.replace('\n', '')
					value = int(l, self.basis)
					if self.test:
						print(value)
					else:
						time.sleep(0.5)
						q.put(value)	
		return 0
			
			
	def terminate(self):
		print("[INFO] Terminating Measurement Thread...")
		self.running = False


def run():
	reading = fromFile(test=True)
	reading.readLoop()	
				
		
if __name__=="__main__":
	run()
