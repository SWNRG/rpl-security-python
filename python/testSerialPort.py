#!/usr/bin/python

import serial
import sys
from getSerialPortCooja import get1stpts
import time



def get_pts_port():
	ser_port = "" # serial port of cooja sink mode
	#ser_port = get1stpts()
	while not ser_port: #if cooja port is not there, dont continue
		try:
			ser_port = get1stpts()
		except Exception as e:
			print ("Cooja Port Error ", e)
	print ("\nCooja port found, continuing...\n")
	ser = serial.Serial(ser_port,  115200)#, timeout = 1)
	return	ser



if __name__ == '__main__':
	s_port = get_pts_port()
	counter = 0
	while counter <20:
		try:	
			readOut = s_port.readline().rstrip('\n')#.decode('ascii')
			print("readOut: ",readOut)
			#s_port.open()
			#s_port.write('{"PTY":"BR","DAT":"100"}')
			#print( "write to ser port")
			s_port.write("GEO\n") # DONT FORGET THE "\n"
			#s_port.close()
			#time.sleep(1)
		except Exception as e:
			print("I/O port exception: ",e)
		counter+=1