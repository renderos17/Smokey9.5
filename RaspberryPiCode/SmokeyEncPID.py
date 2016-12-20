import RPi.GPIO as GPIO
from pyfirmata import Arduino, ArduinoMega, util
import SocketServer
import time

#This code manages the robot itself.
#It also handles communication between the arduino and the motor controller
#Created by Alexis Renderos


GPIO.setmode(GPIO.BCM)

#def arduino board for onboard comms
board = ArduinoMega('/dev/ttyACM0')

#in1-4 are for the arduino to interface with motor controller
	#these determine direction of current
in1pin = board.get_pin('d:22:o')
in2pin = board.get_pin('d:24:o')
in3pin = board.get_pin('d:26:o')
in4pin = board.get_pin('d:28:o')
lDrives = [in1pin, in2pin, in3pin, in4pin]

#for arduino again, this is PWM to attain speed control
enablePin1 = board.get_pin('d:6:p')
enablePin2 = board.get_pin('d:7:p')

#for the arduino servo control::gripper
gripper1 = board.get_pin('d:9:s')

#definiions of two quadrature encoders that operate together
input_A = 18
input_B = 23

input_C = 17
input_D = 22
#encoder1
GPIO.setup(input_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(input_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#encoder2
GPIO.setup(input_C, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(input_D, GPIO.IN, pull_up_down=GPIO.PUD_UP)

old_a = True
old_b = True

old_c = True
old_d = True

cur_L = 0
cur_R = 0


def grip1(a):
    gripper1.write(a)
    print 'gripper changed'

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

def MotorOff():
	in1pin.write(0)
	in2pin.write(0)
	in3pin.write(0)
	in4pin.write(0)
	enablePin1.write(0)
	enablePin2.write(0)
	print 'motoroff'

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
        # result may need to be inverted in code to accomodate wiring scheme
    if resultR != 0 :
        cur_R = cur_R - resultR
         # result may need to be inverted in code to accomodate wiring scheme

    time.sleep(0.001)

# Settings for the Remote server
portListen = 9038

class PicoBorgHandler(SocketServer.BaseRequestHandler):
    # Function called when a new message has been received
    def handle(self):
        global isRunning
		
        request, socket = self.request          # Read who spoke to us and what they said
        request = request.upper()               # Convert command to upper case
        driveCommands = request.split(',')      # Separate the command into individual drives
        if len(driveCommands) == 1:
            # Special commands
            if request == 'ALLOFF':
                # Turn all drives off
                MotorOff()
                print 'All drives off'
            elif request == 'EXIT':
                # Exit the program
                isRunning = False
            else:
                # Unknown command
                print 'Special command "%s" not recognised' % (request)
        elif len(driveCommands) == len(lDrives):
            # For each drive we check the command
            for driveNo in range(len(driveCommands)):
                command = driveCommands[driveNo]
                print driveNo
                if command == 'ON':
                    # Set drive on
                    lDrives[driveNo].write(1)
                    enablePin1.write(1)
                    enablePin2.write(1)
                elif command == 'OFF':
                    # Set drive off
                    lDrives[driveNo].write(0)
                elif command == 'X':
                    # No command for this drive
                    pass
                else:
                    # Unknown command
                    print 'Drive %d command "%s" not recognized!' % (driveNo, command)
        else:
            # Did not get the right number of drive commands
            print 'Command "%s" did not have %d parts!' % (request, len(lDrives))

try:
    global isRunning

    # Start by turning all drives off
    MotorOff()
    raw_input('You can now turn on the power, press ENTER to continue')
    # Setup the UDP listener
    remoteKeyBorgServer = SocketServer.UDPServer(('', portListen), PicoBorgHandler)
    # Loop until terminated remotely
    isRunning = True
    while isRunning:
        remoteKeyBorgServer.handle_request()
    # Turn off the drives and release the GPIO pins
    print 'Finished'
    MotorOff()
    raw_input('Turn the power off now, press ENTER to continue')
    GPIO.cleanup()
except KeyboardInterrupt:
    # CTRL+C exit, turn off the drives and release the GPIO pins
    print 'Terminated'
    MotorOff()
    raw_input('Turn the power off now, press ENTER to continue')
    GPIO.cleanup()
