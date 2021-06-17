# ------------__ Hacking STEM – joystick.py – micro:bit __-----------
#  For use with the How do sharks swim lesson plan from Microsoft
#  Education Workshop at https://aka.ms/shark-lesson
#  http://aka.ms/hackingSTEM
#
#  Uses pins 0,1,2,3,6,7 for direction switches:
#   Roll Counter Clockwise = pin1
#   Roll Clockwise = pin0
#   Pitch Counter Clockwise = pin3
#   Pitch Clockwise = pin2
#   Yaw Counter Clockwise = pin7
#   Yaw Clockwise = pin6
#
#  Warning: The serial interactions on this project are confusing
#
#  This project uses a BBC micro:bit microcontroller, information at:
#  https://microbit.org/
#
#  Comments, contributions, suggestions, bug reports, and feature
#  requests are welcome! For source code and bug reports see:
#  https://github.com/microsoft/hackingstem-bbc-joystick-microbit
#
#  Copyright 2018, Adi Azulay, Jeremy Franklin-Ross, David Myka
#  Microsoft EDU Workshop - HackingSTEM
#  MIT License terms detailed in LICENSE.txt
# ===---------------------------------------------------------------===

from microbit import *

# String which is used to contain joystick state values
current_return_prefix = "{},{},{},".format(0, 0, 0)

# Previously sent joystick state string
last_return_prefix = ""


# Appended to direction information, this constant is used by excel
# to return the shark to "home" position
DEFAULT_RETURN_SUFFIX = ",0,-10.5,0"

# Working variable, which will be updated periodically with new
# position and time information
current_return_suffix = DEFAULT_RETURN_SUFFIX

# Previously sent return suffix
last_return_suffix = ""


# Variables used in dealing with serial in data, created globally
# to reduce instantiation load
serial_in_data = ""
last_serial_in_data = ""
comma_count = 0

# Optimal interval in millisecond to push redundant state
# as serial writes. A heartbeat of data.
SERIAL_WRITE_INTERVAL = 120

# Used track intervals of serial writes
last_serial_write_time = running_time()


# Maximum interval in millisecond to poll the joystick state
JOYSTICK_READ_INTERVAL = int(SERIAL_WRITE_INTERVAL/3)

# Used track intervals of joystick reads
last_joystick_read_time = running_time()

# Constant used to indicate when to reboot the micro:bit
# Rebooting the micro:bit after a long duration helps flush
# serial buffers and reduces frozen interactions... It will also
# teleport the shark to home position once every 45 minutes.
RESET_TIME = running_time() + (1000 * 45) * 60

def read_joystick():
	#   This function read check the switches on the joystick
	#   and assigns either a 1 for counter clockwire turn, a
	#   0 for no turn or -1 for a clockwise turn.

	global current_return_prefix

	# Variables used to track joystick direction, these values
	# are formatted into a string and sent to excel via serial
	pitch = 0
	yaw = 0
	roll = 0

	roll_counterclockwise = pin0.read_digital()
	roll_clockwise = pin1.read_digital()

	pitch_counterclockwise = pin2.read_digital()
	pitch_clockwise = pin3.read_digital()

	yaw_counterclockwise = pin6.read_digital()
	yaw_clockwise = pin7.read_digital()

	if roll_counterclockwise == 1:
		roll = 1
	elif roll_clockwise == 1:
		roll = -1

	if pitch_counterclockwise == 1:
		pitch = 1
	elif pitch_clockwise == 1:
		pitch = -1

	if yaw_counterclockwise == 1:
		yaw = 1
	elif yaw_clockwise == 1:
		yaw = -1

	current_return_prefix = "{},{},{},".format(roll, pitch, yaw)

def process_serial_input():
	# process_serial_input() is complicated in part because the
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
	serial_in_data = ""
	
	while uart.any() is True and (len(serial_in_data) == 0 or not serial_in_data[-1:] == '\n'):  # read entire buffer
		sleep(20) # helps serial buffer fill up
		serial_in_data += str(uart.read(150), "utf-8", "ignore")
		sleep(10)

	# skip if not well formed input
	if (len(serial_in_data) <= 0):
		return

	if (len(serial_in_data) <= 0 or serial_in_data.count(",") != 7 or not serial_in_data.endswith("\n")):
		return  # skip this method if not formed well

	# strip off extra whitespace and commas
	serial_in_data = serial_in_data.replace('\n','').rstrip(' ,\n\r')
	
	# if there's no change, skip the rest of this method
	if last_serial_in_data == serial_in_data: return

	last_serial_in_data = serial_in_data

	current_return_suffix = serial_in_data



def output_to_serial():
	# uart is the micropython serial object
	uart.write(current_return_prefix + current_return_suffix + "\n")

#
# Configs

uart.init(9600)  #initialize serial connection

display.show(Image.ASLEEP) # display friendly face at start or restart
sleep(1000)

display.off() # turn off display so we can access more pins for io

# Main program loop. Will repeat forever (because True is always True)
while True:
	# Only read joystick after read interval time has elapsed
	if ((running_time() - last_joystick_read_time) >= JOYSTICK_READ_INTERVAL):
		last_joystick_read_time = running_time()
		read_joystick()

	process_serial_input()  # read from serial and do things

	# if there's a change, send update immediately otherwise,
	# maintain a steady pulse at SERIAL_WRITE_INTERVAL
	if ( (last_return_prefix != current_return_prefix)
	or (last_return_suffix != current_return_suffix)
	or (running_time() - last_serial_write_time) >= SERIAL_WRITE_INTERVAL):
		last_serial_write_time = running_time()
		last_return_prefix = current_return_prefix
		last_return_suffix = current_return_suffix
		output_to_serial()      # write data to serial for excel to use

		# Reseting board if it has been running a long time
		# helps prevent serial issues
		if (running_time() > RESET_TIME ):
			reset()
