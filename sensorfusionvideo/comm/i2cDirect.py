####################################
# Skript to read and write I2C data
# using the Python smbus
#
# Author: Arasch Lagies
# First Version: 3/13/2020
# Last Update: 3/13/2020
#
#####################################
import smbus
import time
import math

from threading import Thread
import matplotlib.animation as animation

CHANNEL = 1			# I2C bus
ADDR    = 0x70      # I2C address of the connected device
WRITEREG = 0xe0     # Address to which to write to, to request measurement...
REQVAL   = 0x51     # Value for measurement request...
READREG  = 0xe0     # Address from which to read from, to get data...


class i2c(Thread):
	def __init__(self, channel=CHANNEL, addr=ADDR, plotLength=100, numPlots=1):
		self.bus = smbus.SMBus(channel)    	# I2C bus...
		self.address = addr					# Address of the target device...
		self.isReceiving = False			# Flag for indicating if background process is receiving data
		self.thread = None                  # Flag for inndicating if thread is running
		self.previousTimer = 0
		self.numPlots = numPlots
		self.isRun = True
			
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
		
	def readI2CStart(self):
		if self.thread == None:
			self.thread = Thread(target=self.backgroundThread)
			self.thread.start()
			# Block untill start of receiving values
			while self.isReceiving != True:
				print("Waiting...")
				time.sleep(0.1)
				
	
			
	def backgroundThread(self):
		print("Starting background thread")
		time.sleep(1.0)    # Buffer delay...
		# Run infinite loop for measurements...
		while(self.isRun):
			self.rawData = self.range()
			#print(f"Received {self.rawData} cm")
			self.isReceiving = True
		
		
		
def run():
	device = i2c()
	while(True):
		val = device.range()
		print(f"[INFO] Measued : {val} cm ")
		time.sleep(0.3)
		
		
if __name__=="__main__":
	run()
