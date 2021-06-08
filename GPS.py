import serial
import pynmea2

class GPS():
	def __init__(self, port="/dev/ttyAMA1") -> None:
		self.ser=serial.Serial(port, baudrate=9600)
		self.dataout = pynmea2.NMEAStreamReader()

	def read_loc(self):
		while True:
			newdata=self.ser.readline().decode('ascii')
			if newdata[0:6] == "$GPGGA":
				newmsg=pynmea2.parse(newdata)
				lat=newmsg.latitude
				lng=newmsg.longitude
				if lat != 0 and lng != 0:
					return [lat, lng]