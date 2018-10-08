# ------------__ Hacking STEM – joystick.py – micro:bit __-----------
#  For use with the How do sharks swim lesson plan from Microsoft
#  Education Workshop at http://aka.ms/hackingSTEM
# 
#  Uses pins 0,1,2,3,6,7
#   Roll Counter Clockwise = pin1
#   Roll Clockwise = pin0
#   Pitch Counter Clockwise = pin3
#   Pitch Clockwise = pin2
#   Yaw Counter Clockwise = pin7
#   Yaw Clockwise = pin6
#
#  Note: This project has a counter intuitive relationship with 
#  excel. Much of the code is to handle serial data from excel
#  which is immediately returned to it in subsequent serial writes.
#
#  This project uses a BBC micro:bit microcontroller, information at:
#  https://microbit.org/
#
#  Comments, contributions, suggestions, bug reports, and feature
#  requests are welcome! For source code and bug reports see:
#  http://github.com/[TODO github path to Hacking STEM]
#
#  Copyright 2018, Adi Azulay w/ contributions by Jeremy Franklin-Ross
#  Microsoft EDU Workshop - HackingSTEM
#  MIT License terms detailed in LICENSE.txt
# ===---------------------------------------------------------------===

from microbit import *

# Used by excel to home shark graphic
DEFAULT_RETURN_STRING = ",0,-10.5,0" 

# Working variable 
current_return_string = DEFAULT_RETURN_STRING  

# Variables used in dealing with serial in data 
parsed_data = "" 
last_data = ""
comma_count = 0

# How often we poll joystick
last_read = running_time() 
SENSOR_INTERVAL = 100

#  Directional Variables
pitch = 0
yaw = 0
roll = 0


def processSensors():

	#   This function read check the switches on the joystick
	#   and assigns either a 1 for counter clockwire turn, a
	#   0 for no turn or -1 for a clockwise turn.

	global roll, pitch, yaw

	roll_ccw = pin1.read_digital()
	roll_cw = pin0.read_digital()

	pitch_ccw = pin3.read_digital()
	pitch_cw = pin2.read_digital()

	yaw_ccw = pin7.read_digital()
	yaw_cw = pin6.read_digital()

	if roll_ccw == 1:
		roll = 1
	elif roll_cw == 1:
		roll = -1
	else:
		roll = 0

	if pitch_ccw == 1:
		pitch = 1
	elif pitch_cw == 1:
		pitch = -1
	else:
		pitch = 0

	if yaw_ccw == 1:
		yaw = 1
	elif yaw_cw == 1:
		yaw = -1
	else:
		yaw = 0

def getData():
	global current_return_string, parsed_data, last_data
	
	while uart.any() is True: # and parsed_data.count('\n') == 0: 
		parsed_data += str(uart.read(150), "utf-8", "ignore")
		sleep(10)

	# make sure we have a well formed serial read.
	comma_count = parsed_data.count(",") 

	if ( comma_count != 7):
		parsed_data = ""
		return  # skip this method if not formed well


	if len(parsed_data) > 0 and parsed_data.endswith("\n"):
		parsed_data = parsed_data.rstrip(',\n\r')
		parsed_data = parsed_data.rstrip()
		
		# if there's no change, skip the rest of this method
		if last_data == parsed_data: 
			parsed_data = ""
			return

		last_data = parsed_data

		if parsed_data.endswith(",1"):  # reset to home value 
			current_return_string = DEFAULT_RETURN_STRING 
		elif parsed_data.endswith(",0"):
			current_return_string = parsed_data 

		parsed_data = ""


uart.init(9600)
display.off()

while True:
	if (running_time() - last_read >= SENSOR_INTERVAL):
		last_read = running_time() 
		processSensors()

	getData()

	uart.write("{},{},{},".format(roll, pitch, yaw)) 
	uart.write(current_return_string)
	uart.write("\n")

	sleep(10)
