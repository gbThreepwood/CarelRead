#!/usr/bin/python
# Test kommunikasjon med Carel ir32
# Eirik Haustveit, 2016

import serial
import io
import time

import argparse
import logging

import signal
import sys

def signal_handler(signal, frame):
	print('Keyboard interrupt')
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)



parser = argparse.ArgumentParser(description='Request sensor status from Carel IR32 controller, and decode the returned message.')

parser.add_argument('-b','--baudrate', type=int, help='Communication baudrate for the serial connection (default 19200).')
parser.add_argument('-a', '--address', help='Address of the Carel IR32 controller', type=int, choices=range(0,16))
parser.add_argument('-p','--port', help='Serial port interface to use, e.g. /dev/ttyUSB0')
parser.add_argument('-d','--device', help='Device to read (IR32 or IR33)')
parser.add_argument('-q','--query', help='Ask the device for firmware version.')

args = parser.parse_args()


# assuming loglevel is bound to the string value obtained from the
# command line argument. Convert to upper case to allow the user to
# specify --log=DEBUG or --log=debug
#umeric_level = getattr(logging, loglevel.upper(), None)
#if not isinstance(numeric_level, int):
#    raise ValueError('Invalid log level: %s' % loglevel)
#logging.basicConfig(level=numeric_level, ...)


def main():
	try:
		ser = serial.Serial(args.port, timeout=0.01)
	
		ser.bytesize = serial.EIGHTBITS #number of bits per bytes
		ser.parity = serial.PARITY_NONE #set parity check: no parity
		ser.stopbits = serial.STOPBITS_TWO #number of stop bits
		ser.xonxoff = False     #disable software flow control
		ser.rtscts = False     #disable hardware (RTS/CTS) flow control
		ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
		ser.writeTimeout = 0.1     #timeout for write
		
		ser.baudrate = args.baudrate

		logging.info(ser.name)
		logging.info('Nyttar hastigheita: ' + str(ser.baudrate))
	

		if args.query == '1':
			enquire_firmware(args.address, ser)	
		else:	
			read_temperature(args.address, ser)
		
		ser.close()
	except:
		logging.error('Undefined error.')
	

def compute_crc(command):
	crc = '\x37\x35'
	return crc
	
def enquire_firmware(address, ser):
	command = '\x02' + str(args.address) + '\x3f\x03'	
	crc = compute_crc(command) 
	
	logging.info('Firmware version query')
	ser.write(command  + crc)
	response = ser.readline()
	if not response:
		print('Communication failure')
	else:	
		print('Communication OK. FW: ' + response[1:3])


def read_temperature(address, ser):
	logging.info('Adresse: ' + str(address))


	logging.info('Requesting status')	
	ser.write('\x05' + str(address))
	time.sleep(0.01)

	logging.info('Reasing return message')
	return_msg = ser.readline()
	if not return_msg:
		print(-1)
		#logging.warning('Communication error, did not receive any data.')
	else:
		logging.info(return_msg)
		logging.info(":".join("{:02x}".format(ord(c)) for c in return_msg))

		# Extract the temperature of sensor 1 from the return message.
		if args.device == 'IR33':	
			temp = int(return_msg[7:9],16)
		else:
			temp = int(return_msg[6:8],16)
		

		temp = temp/10.0
		logging.info('Temperatur: ' + str(temp))
		print(str(temp))

if __name__ == '__main__':
	main()
