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

# Appended to direction information, this constant is used by excel
# to return the shark to "home" position
DEFAULT_RETURN_SUFFIX = ",0,-10.5,0" 

# Working variable, which will be updated periodically with new
# position and time information
current_return_suffix = DEFAULT_RETURN_SUFFIX  

# Variables used in dealing with serial in data, created globally
# to reduce instantiation load
serial_in_data = "" 
last_serial_in_data = ""
comma_count = 0

# Maximum interval in millisecond to poll the joystick state
JOYSTICK_READ_INTERVAL = 100

# Used track intervals of joystick reads
last_joystick_read_time = running_time() 

# Constant used to indicate when to reboot the micro:bit
# Rebooting the micro:bit after a long duration helps flush 
# serial buffers and reduces frozen interactions... It will also 
# teleport the shark to home position once every 45 minutes.
RESET_TIME = running_time() + (1000 * 45) * 60

# Variables used to track joystick direction, these values
# are sent to excel via serial 
pitch = 0
yaw = 0
roll = 0

def read_joystick():

	#   This function read check the switches on the joystick
	#   and assigns either a 1 for counter clockwire turn, a
	#   0 for no turn or -1 for a clockwise turn.

	global roll, pitch, yaw

	roll_counterclockwise = pin1.read_digital()
	roll_clockwise = pin0.read_digital()

	pitch_counterclockwise = pin3.read_digital()
	pitch_clockwise = pin2.read_digital()

	yaw_counterclockwise = pin7.read_digital()
	yaw_clockwise = pin6.read_digital()

	if roll_counterclockwise == 1:
		roll = 1
	elif roll_clockwise == 1:
		roll = -1
	else:
		roll = 0

	if pitch_counterclockwise == 1:
		pitch = 1
	elif pitch_clockwise == 1:
		pitch = -1
	else:
		pitch = 0

	if yaw_counterclockwise == 1:
		yaw = 1
	elif yaw_clockwise == 1:
		yaw = -1
	else:
		yaw = 0
def process_serial_input():
	# process_serial_input() is complicated because the shark 
	# spreadsheet produces messages faster than we can handle 
	# 
	# We receive a high number of malformed lines from serial, which 
	# are eliminated by simple heuristics (comma count and end 
	# character check).
	#
	# We also avoid unnecessary processing by comparing current message 
	# to last parsed message.
	#
	# Additionally, to mitigate processing impact of this we avoid any 
	# parsing of values and simply inspect last few characters to 
	# determine if game state reset is required.
	global current_return_suffix, serial_in_data, last_serial_in_data
	
	while uart.any() is True:  # read entire buffer
		serial_in_data += str(uart.read(150), "utf-8", "ignore")
		sleep(10)

	# skip if not well formed input
	if (len(serial_in_data) <= 0 or serial_in_data.count(",") != 7 or not serial_in_data.endswith("\n")): 
		serial_in_data = ""
		return  # skip this method if not formed well

	# strip off extra stuff
	serial_in_data = serial_in_data.rstrip(',\n\r')
	serial_in_data = serial_in_data.rstrip() # TODO necessary?
	
	# if there's no change, skip the rest of this method
	if last_serial_in_data == serial_in_data: 
		serial_in_data = ""
		return

	last_serial_in_data = serial_in_data

	if serial_in_data.endswith(",1"):    
		# on reset flag, use default return suffix 
		current_return_suffix = DEFAULT_RETURN_SUFFIX 
	elif serial_in_data.endswith(",0"):  
		# w/ no reset flag update return suffix received string
		current_return_suffix = serial_in_data 

	serial_in_data = ""

def output_to_serial():
	# uart is the micropython serial object
	uart.write("{},{},{},".format(roll, pitch, yaw)) 
	uart.write(current_return_suffix)
	uart.write("\n")

uart.init(9600)  #initialize serial connection

display.show(Image.ASLEEP) # display friendly face at start or restart
sleep(1000) 

display.off() # turn off display so we can access more pins for io

# Main program loop. Will repeat forever (because True is always True)
while True:
	# Only read joystick after read interval time has elapsed
	if ( (running_time() - last_joystick_read_time) >= JOYSTICK_READ_INTERVAL):
		last_joystick_read_time = running_time() 
		read_joystick()

		# Reseting board if it has been running a long time 
		# helps prevent serial issues 
		if (running_time() > RESET_TIME ):
			reset()

	process_serial_input()  # read from serial and do things
	output_to_serial()      # write data to serial for excel to use
	sleep(10)               # reduce buffer overrun to excel
