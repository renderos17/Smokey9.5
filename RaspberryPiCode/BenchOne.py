import RPi.GPIO as GPIO
from pyfirmata import Arduino, ArduinoMega, util
import time

GPIO.setmode(GPIO.BCM)

#def arduino board for onboard comms
board = ArduinoMega('/dev/ttyACM0')

#in1-4 are for the arduino to interface with motor controller
	#these determine direction of current
in1pin = board.get_pin('d:22:o')
in2pin = board.get_pin('d:24:o')
in3pin = board.get_pin('d:26:o')
in4pin = board.get_pin('d:28:o')

#for arduino again, this is PWM to attain speed control
enablePin1 = board.get_pin('d:6:p')
enablePin2 = board.get_pin('d:7:p')

#determines encoder pins
input_A = 17
input_B = 22

input_C = 18
input_D = 23

GPIO.setup(input_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(input_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(input_C, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(input_D, GPIO.IN, pull_up_down=GPIO.PUD_UP)

old_a = True
old_b = True

old_c = True
old_d = True

cur_L = 0
cur_R = 0
#end of encoder pin defs

#Takes a motor speed from 0-255 and direction of current (0,1) to be output
def setMotor1(speed, direction):
	if direction == 1:
		in1pin.write(1)
		in2pin.write(0)
	elif direction == 0:
		in1pin.write(0)
		in2pin.write(1)
	#elif
		#Kills motors if unintelligible request
		#in1pin.write(0)
		#in2pin.write(0)

	enablePin1.write(speed/255.0)
	#print(speed/255.0)
	
#Takes a motor speed from 0-255 and direction of current (0,1) to be output
def setMotor2(speed, direction):
	if direction == 1:
		in3pin.write(1)
		in4pin.write(0)
	elif direction == 0:
		in3pin.write(0)
		in4pin.write(1)
	#else
		#Kills motors if unintelligible request
		#in3pin.write(0)
		#in4pin.write(0)

	enablePin2.write(speed/255.0)
	#print(speed/255.0)

# gets the current encoder values from both sides
# values are stored in global 'resultL' and 'resultR'
# raw data saved
def getEncoder():
	global old_a, old_b, old_c, old_d
	global cur_L, cur_R
	resultL = 0
	resultR = 0
	
	new_a = GPIO.input(input_A)
	new_b = GPIO.input(input_B)
	new_c = GPIO.input(input_C)
	new_d = GPIO.input(input_D)
	
	if new_a != old_a or new_b != old_b :
		if old_a == 0 and new_a == 1 :
			resultL = (old_b * 2 - 1)
		elif old_b == 0 and new_b == 0:
			resultL = -(old_b * 2 - 1)
	old_a, old_b = new_a, new_b
	
	if new_c != old_c or new_d != old_d :
		if old_c == 0 and new_c == 1 :
			resultR = (old_d * 2 - 1)
		elif old_d == 0 and new_d == 0:
			resultR = -(old_d * 2 - 1)
	old_c, old_d = new_c, new_d
	
	if resultL != 0 :
		cur_L = cur_L + resultL
		
	if resultR != 0 :
		cur_R = cur_R - resultR
		 # result inverted in code to accomodate wiring scheme
	print(str(cur_L) + " " + str(cur_R))
	#time.sleep(0.001)
	
while True:
	#Robot Periodic Block Begin
	setMotor1(255,0)
	setMotor2(255,0)
	#for i in range(0, 256):
		#setMotor1(i,0)
		#setMotor2(i,0)
		#print('done')
		#getEncoder()
		#time.sleep(0.01)
	#for i in range(0, 256):
		#setMotor1(i,1)
		#setMotor2(i,1)
		#print('done')
		#getEncoder()
		#time.sleep(0.01)
	#Robot Periodic Block End

