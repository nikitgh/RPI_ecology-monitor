#!bin/python3
import serial
import time
import numpy as np

class PMSensor():
	
	def __init__(self, port, env):
		# gpio serial port
		self.port = port 
		# sensor placed indoor/outdoor (0/1)
		self.standard = env
		# hardcode the baudrate
		self.baudrate = 9600
		# enable software flow control.
		self.xonxoff = True
		# timeout
		self.timeout = 0
		self.serial = None
		self.sensor_wakeup = False

	def open_port(self, force=False):
	
		# open serial port
		# try:
		if force:
			self.serial = serial.Serial(self.port, baudrate=self.baudrate, xonxoff=self.xonxoff, timeout=self.timeout)
		elif self.serial == None:
			self.serial = serial.Serial(self.port, baudrate=self.baudrate, xonxoff=self.xonxoff, timeout=self.timeout)
		elif not self.serial.is_open:
			self.serial = serial.Serial(self.port, baudrate=self.baudrate, xonxoff=self.xonxoff, timeout=self.timeout)
		else:
			# print("not opened")
			pass
			
		# except

	def fixed_bytes(self):
		
		while True:
		
			#get two starting bytes
			start_bytes = self.serial.readline(2)
			start_bytes_hex = start_bytes.hex()
			
			#check for fixed characters
			if start_bytes_hex == '424d':
				return True 

	def read_serial(self):
		
		# read from uart, up to 22 bytes
		data_uart = self.serial.readline(22)
		
		# encode
		data_hex = data_uart.hex()
		
		# calculate pm values
		# indoor
		if self.standard == 0:
			pm1  = int(data_hex[4] + data_hex[5] + data_hex[6] + data_hex[7], 16)
			pm25 = int(data_hex[8] + data_hex[9] + data_hex[10] + data_hex[11], 16)
			pm10 = int(data_hex[12] + data_hex[13] + data_hex[14] + data_hex[15], 16)
		# outdoor
		elif self.standard == 1:
			pm1  = int(data_hex[16] + data_hex[17] + data_hex[18] + data_hex[19], 16)
			pm25 = int(data_hex[20] + data_hex[21] + data_hex[22] + data_hex[23], 16)
			pm10 = int(data_hex[24] + data_hex[25] + data_hex[26] + data_hex[27], 16)
        
		# store values in a list
		values = [pm1, pm25, pm10]
        
		# close serial port
		# self.serial.close()
		
		# return data
		return values

	def write_serial(self, cmd, timeout=0):
		
		# open serial port
		self.open_port()
		
		# writes binary data to the serial port
		write = self.serial.write(cmd)
		
		# close serial port
		# self.serial.close()
		
		# set timeout
		time.sleep(timeout)

	def single_read(self, force=False):
		
		# open serial port
		self.open_port(force)
		
		while True:
			# the number of bytes in the input buffer should be non-zero to avoid errors
			if self.serial.inWaiting() > 0:
			
				# validate generated data
				if self.fixed_bytes() == True:
				
					# get the pm values
					data = self.read_serial()
					
					# close serial port
					# self.serial.close()
				
				# data read-out
				return data
	
	def read_pm(self, no_passive_mode = False, force=False):
		
		if not self.sensor_wakeup or not no_passive_mode:
			print("wakeup")
			self.wakeup()
		else:
			print("no wakeup")

		try:
			data = self.single_read(force)
		except IndexError:
			print("error index")
			return self.read_pm()

		if not no_passive_mode:
			self.passive_mode()
		
		# return data
		return data

	def wakeup(self):
		self.sensor_wakeup = True

		# wakeup sensor with 45sec timeout
		self.write_serial(b'BM\xe4\x00\x01\x01t', 45)
		# put into active mode
		self.write_serial(b'BM\xe1\x00\x01\x01q', 15)

	def passive_mode(self):
		self.sensor_wakeup = False

		# put the sensor in the passive mode
		self.write_serial(b'BM\xe1\x00\x00\x01p')
		
		# standby mode, aka. sleep
		self.write_serial(b'BM\xe4\x00\x00\x01s')

	
