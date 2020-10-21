import sys

#Math libraries
import statistics as stat
import numpy as np

#String library
import readchar

#Library to connect to DMM
import socket 

import argparse 

#Time/date libraries
import time
import datetime
from datetime import datetime

###					###
### Test Parameters ### 
###					###

#Frequency that data is read in (s)
READ_FREQUENCY = 1

#IP address for DMM 
DMM_IP_ADDRESS = '192.168.86.120'

### Instrument Connection ###
class Instrument():

	#Initialize instrument object with IP address passed in
	def __init__(self, ip_address):
		self.ip_address = ip_address

	#Initialize connection to the DMM
	def instrument_connect(self): 
		self.name = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.name.connect((self.ip_address,5025))
		self.name.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY,1)
		self.name.settimeout(2)
		identify = '*IDN?\n'
		self.name.send((identify.encode('utf-8')))
		print('DMM connected')

	#SCPI command to DMM to measure voltage

	#0.1 => 100mV range, 1 => 1V range, 10 => 10V range
	def DMM_voltage(self):
		DMM_voltage = 'MEAS:VOLT:DC? 10\n'
		self.name.send(DMM_voltage.encode('utf-8'))

	#SCPI command to DMM to measure current
	def DMM_current(self):
		DMM_current = 'MEAS:CURR:DC? 10, DEF\n'
		self.name.send(DMM_current.encode('utf-8'))

	#Command to recieve measurement from DMM as a string
	def measurement_read(self):
		try:
			#DMM data comes in with 2 columns, need to split string so only the number is recieved
			data_arr = self.name.recv(1000).split(b'\n')
			data = float(data_arr[0])
			data = str(data)
		
		except: 
			data = '0.0'

		return data 

### Gathering and formatting data ###

def log_data(data_file): #data_file
	global count, current_time, s1, previous_time, test_time
	
	#Send DMM command to measure voltage/current
	s1.DMM_voltage()

	#Get measurement
	voltage = s1.measurement_read()
	
	#Put together all data points 
	data_str = str(count) + ',' + str(test_time) +','+ voltage + '\n'

	#Time Operations
	current_time = float(time.time())
	time_delta = current_time - previous_time
	test_time = test_time + time_delta
	previous_time = time.time()

	#Update Counter
	count = count + 1 
	
	#Write to data file 
	data_file.write(data_str)

	#Print data file to command prompt so you can see data collected
	print(data_str)
	return data_file

#Get current time/data
now               = datetime.now() 
#Format data file name
date_time         = now.strftime("%Y%m%d__%H%M%S_")
#Make csv file name
test_file_name    = date_time+"DMM_log.csv"
#Open test file to be able to add data
test_file         = open(test_file_name,"w") #create data file 
#Write column headers
test_file.write("Count,Test Time [s], Voltage [V]\n")

def main(argv):
	global tst_time, count, time_0, previous_time, test_time, s1

	### Initiate DMM connection ###
	s1 = Instrument(ip_address = DMM_IP_ADDRESS)
	s1.instrument_connect()

	### Initialize time/counters ###
	count = 0
	previous_time = time.time()
	test_time = 0.0

	### Main Loop ###

	#while(1) makes it run forever, to stop it, do ctrl + C
	while(1):
		#log data and pass the csv file into log_data function
		data_str = log_data(test_file)
		#this sets the time for time between reads
		time.sleep(READ_FREQUENCY)

if __name__ == "__main__":
	main(sys.argv)