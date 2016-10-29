import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)

input_A = 18
input_B = 23

input_C = 17
input_D = 22

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

def getEncoder():
	# gets the current encoder values from both sides
	# values are stored in global 'resultL' and 'resultR'
	# raw data saved
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

	time.sleep(0.001)
	

x = 0

while True:
	getEncoder()
	print(str(cur_L) + " " + str(cur_R))

