#   Joystick Controller Code for Microsoft HackingSTEM + BBC Lesson
#   For more information go to aka.ms/hackingstem
#   V1.2
#   Change Log
#   - Reset Function Included
#   - gameState changed to hitTime
#   - isensor nput pairs reversed
#
#   Written by Adi Azulay
#   Copyright 2018 Microsoft

from microbit import *

DEFAULT_RETURN_STRING = ",0,-10.5,0"
current_return_string = DEFAULT_RETURN_STRING
parsed_data = ""
comma_count = 0
last_read = running_time() 
SENSOR_INTERVAL = 250
last_data = ""

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

in_data = ""
def getData():
	#   This function gets data from serial and builds it into a string
	#TX,0,-3,0,0,,,,,,,
	global current_return_string, parsed_data, last_data
	

	while uart.any() is True: # and parsed_data.count('\n') == 0: 
		parsed_data += str(uart.read(150), "utf-8", "ignore")
		sleep(10)

	comma_count = parsed_data.count(",")

	# if (comma_count > 11 or comma_count < 7):
	if ( comma_count != 7):
		# uart.write("{},{},{},".format(roll, pitch, yaw)) 
		# uart.write(current_return_string)
		# uart.write(",,,,,,,FAILED   FFFFFFFF   FAILED:" + parsed_data[:-1] + "###" + str(comma_count) + "###\n")
		parsed_data = ""
		return


	if len(parsed_data) > 0 and parsed_data.endswith("\n"):
		parsed_data = parsed_data.rstrip(',\n\r')
		parsed_data = parsed_data.rstrip()
		
		if last_data == parsed_data:
			return

		last_data = parsed_data

		if parsed_data.endswith(",1"):
			current_return_string = DEFAULT_RETURN_STRING + ",RESET  rrrrrrrrrrrrrrrrrr RESET" + str(comma_count) + "#"
			#uart.write("current now DEFAULT {}".format(current_return_string)+"\n")
		elif parsed_data.endswith(",0"):
			current_return_string = parsed_data + ",UPDATE T:" + str(running_time()) + "#" + str(comma_count) + "#"
			#:-1 peels off the "\n"
			#uart.write("current now parsed {}".format(current_return_string)+"\n")
		else:
			uart.write("{},{},{},".format(roll, pitch, yaw)) 
			uart.write(current_return_string)
			uart.write(",,,,,,,,ERROR    EEEEEEEE      ERROR:," + parsed_data + "###\n")
		parsed_data = ""
		# sleep(500)
		

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
	# sleep(250)

#	print("{},{},{},{}"roll, pitch, yaw, current_return_string)
	sleep(10)
