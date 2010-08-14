# hicompass module - for interfacing with 
# the HiTechnic Lego Mindstorms NXT compass sensor
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

#Get the sensor library independent of whether hicompass is in the nxt directory
try:
	import sensor
except:
	import nxt.sensor as sensor
import sys
from nxt.error import DirProtError
from time import sleep

# I2C addresses for a HiTechnic compass sensor
I2C_ADDRESS_CMPS_NX = {
	0x00: ('version', 8, True),
	0x08: ('manufacturer', 8, True),
	0x10: ('sensor_type', 1, True),
	0x41: ('mode_control', 1, True),
	0x42: ('heading_msb', 1, False),
	0x43: ('heading_lsb', 1, False),
	0x44: ('heading', 2, True),
}

class _MetaCMPS_Nx(sensor._Meta):
	'Metaclass which adds accessor methods for CMPS-Nx I2C addresses'

	def __init__(cls, name, bases, dict):
		super(_MetaCMPS_Nx, cls).__init__(name, bases, dict)
		for address in I2C_ADDRESS_CMPS_NX:
			name, n_bytes, set_method = I2C_ADDRESS_CMPS_NX[address]
			q = sensor._make_query(address, n_bytes)
			setattr(cls, 'get_' + name, q)
			if set_method:
				c = sensor._make_command(address)
				setattr(cls, 'set_' + name, c)

class CompassSensor(sensor.DigitalSensor):

	__metaclass__ = _MetaCMPS_Nx

	def __init__(self, brick, port):
		super(CompassSensor, self).__init__(brick, port)
		self.sensor_type = sensor.Type.LOW_SPEED_9V
		self.mode = sensor.Mode.RAW
		self.set_input_mode()
		sleep(0.1)	# Give I2C time to initialize

	
	def get_manufacturer(self):
		return string(self.i2c_query(0x00,8));
	
	def get_sample(self,numtries=5):
		tries = numtries
		heading = 10000
		while heading > 360 or heading < 0:
			try:
				data = self.i2c_query(0x44,2)
				heading = ord(data[0]) + 255*ord(data[1])
			except DirProtError:
				heading = 10000
				tries -= 1
				if tries < 0:
					errstr = "Error: " + str(numtries) + " consecutive bus failures. \nCheck your compass's connection"
					sys.exit(errstr)
				
		return heading
	
	def get_relative_heading(self,target=0):
		rheading = self.get_sample()-target
		if rheading > 180:
			rheading -= 360
		elif rheading < -180:
			rheading += 360
		return rheading	
	
	#this deserves a little explanation:
	#if max > min, it's straightforward, but
	#if min < max, it switches the values of max and min
	#and returns true iff heading is NOT between the new max and min
	def is_in_range(self,min,max):
		reversed = False
		if min > max:
			(max,min) = (min,max)
			reversed = True
		heading = self.get_sample()
		in_range = (heading > min) and (heading < max)
		#an xor handles the reversal
		#a faster, more compact way of saying
		#if !reversed return in_range
		#if reversed return !in_range
		return bool(reversed) ^ bool(in_range) 

	def calibrate_mode(self):
		self.i2c_command(0x41,0x43)

	def measure_mode(self):
		self.i2c_command(0x41,0x00)
	
