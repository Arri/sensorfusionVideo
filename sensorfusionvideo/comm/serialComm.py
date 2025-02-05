##############################################
# Script for serial communication with remote decice
# Arasch Lagies, Axiado
#
# First Verdsion: 3/19/2020
# Last Update: 3/19/2020
#
##############################################
import os
import subprocess
import serial

PORT = "/dev/ttyUSB0"


class Comm():
	def __init__(self, port=PORT):
		self.running = True					# Flag to run and terminate while loop
		self.ser = serial.Serial(port, baudrate= 115200, 
								 bytesize=8, timeout=2)
		# Opening the communication
		#self.ser.open()
		#if not self.ser.is_open:
		#	print(f"[ERROR] The port {port} could not be opened.")
		#	exit(0)
			
	def readByte(self):
		return self.ser.readline()
		
	def readLoop(self, q):
		value = 0
		while(self.running):
			try:
				value = self.readByte()
			except:
				pass
			q.put(value)	
	
	def terminate(self):
		print("[INFO] Terminating Measurement Thread...")
		self.running = False
		
	
def run():
	com = serComm()
	while(True):
		print(com.readByte())

	
if __name__=="__main__":
	run()
