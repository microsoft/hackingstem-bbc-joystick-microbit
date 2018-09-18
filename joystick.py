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

dataIn = ""
parsedData = [0] * 5

#   This should match the number of channels in Data Streamer
numberOfInputChannels = 7

#  Directional Variables
pitch = 0
yaw = 0
roll = 0

#  Input Values from Excel
x = 0
y = 0
z = 0
hitTime = 0

#   Setup Control Variable
n = 0
reset = 0


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
    #   This function gets data from serial and builds it into a string
    global parsedData, builtString
    global dataIn
    builtString = ""
    while uart.any() is True:
        byteIn = uart.read(1)
        if byteIn == b'\n':
            continue
        byteIn = str(byteIn)
        splitByte = byteIn.split("'")
        builtString += splitByte[1]
    parseData(builtString)


def parseData(s):
    #   This function seperates the string into an array
    global parsedData
    if s != "":
        parsedData = s.split(",")


def assignData():
    #   This function assigns data to variable
    #   There is exception handeling in this process
    #   to ensure board doesn't crash due to errors
    global x, y, z, hitTime, reset, parsedData
    try:
        x = parsedData[0]
        y = parsedData[1]
        z = parsedData[2]
        hitTime = parsedData[3]
        reset = parsedData[4]
    except IndexError:
        return


def sendData():
    #   Send data to serial
    print(roll, pitch, yaw, x, y, z, hitTime, sep=',')


def resetGame():
    global x, y, z, hitTime
    x = ""
    y = "0"
    z = "-10.5"
    hitTime = "0"


while n < 1:
    uart.init(9600)
    n = 1


while True:
    processSensors()
    getData()
    assignData()
    if reset == "1":
        resetGame()
    sendData()
    sleep(10)
