####################################
# Skript to read and write I2C data
# using the Python smbus
#
# Author: Arasch Lagies, Axiado
# First Version: 3/13/2020
# Last Update: 3/13/2020
#
#####################################
import smbus
import time
import math
import subprocess

#from threading import Thread
import matplotlib.animation as animation

CHANNEL = 1			# I2C bus
ADDR    = 0x70      # I2C address of the connected device
WRITEREG = 0xe0     # Address to which to write to, to request measurement...
REQVAL   = 0x51     # Value for measurement request...
READREG  = 0xe0     # Address from which to read from, to get data...


class Comm():
	def __init__(self, channel=CHANNEL, addr=ADDR ):
		self.sensorFound = True
		self.running = True					# Flag to run and terminate while loop
		self.channel = channel
		self.address = addr					# Address of the target device...
		i2cs = self.findDevice()

		if len(i2cs) > 0:
			self.bus = smbus.SMBus(channel)    	# I2C bus...
			time.sleep(0.2)
		else:
			self.sensorFound = False
			
	def findDevice(self):
		i2cs = []
		clean = []
		lines = []
		try:
			p = subprocess.Popen(['i2cdetect', '-y',str(self.channel)],stdout=subprocess.PIPE,)
			for i in range(9):
				line = str(p.stdout.readline())
				lines.append(line[5:-4])
			lines.remove(lines[0])
			for i in lines:
				clean.extend(i.split(" "))
			for row in clean:
				if row.isnumeric():
					i2cs.append(row)
			print(f"[INFO] Found device(s) following i2c addesse(s): {','.join(i2cs)}")
		except:
			print(f"[INFO] Could'd not find an I2C device connected on chanell {self.channel}.")
			print("[INFO] Will run data simulation...")
			pass
		return i2cs
		
	def writeByte(self, wreg=WRITEREG, value=REQVAL):
		""" Write the byte of data REQVAL to device at addr at register
		    location WRITEREG. """
		if value > (2**8-1) or value < 0:
			print(f"[ERROR] The value to be written to the device is not a byte")
			return -1
		self.bus.write_byte_data(self.address, wreg, value)
		return 1
		
	def writeWord(self, wreg=WRITEREG, value=REQVAL):
		""" Write a word of data REQVAL to device at addr at register
		location WRITEREG
		"""
		if value > (2**16-1) or value < 0:
			print(f"[ERROR] The value to be written to the device is not a word")
			return -1
		self.bus.write_word_data(self.address, wreg, value)
		return 1
		
	def readByte(self, rreg=READREG):
		""" Read a byte of data from device addr from register READREG """
		value = self.bus.read_byte_data(self.address, rreg)
		return value
		
	def readWord(self, rreg=READREG):
		""" Read a word of data from device addr from register READREG """
		value = self.bus.read_word_data(self.address, rreg)
		return value
		
	def range(self):
		""" Perform a range measurement with the attched I2C Max-Sonar 
		range-finder.
		
		"""
		self.writeByte()			# Request a measurement...
		time.sleep(0.1)				# At least 80ms required untill meas ready...
		value = self.readWord()		# Get the last reported range value
		return value		
		
	def readLoop(self, q):
		value = 0
		if self.sensorFound:
			while(self.running):
				try:
					value = self.range()
				except:
					pass
				q.put(value)
		else:
			while(self.running):
				value += 1      # Test value in case there is no sensor attached
				time.sleep(0.2)
				q.put(value)	
		
	def terminate(self):
		print("[INFO] Terminating Measurement Thread...")
		self.running = False
		
		
		
		
def run():
	device = i2c()
	while(True):
		val = device.range()
		print(f"[INFO] Measued : {val} cm ")
		time.sleep(0.3)
		
		
if __name__=="__main__":
	run()
