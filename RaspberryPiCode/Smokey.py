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

#for the arduino servo control::gripper
gripper = board.get_pin('d:9:s')

lOutputs = [in1pin, in2pin, in3pin, in4pin, leftSpeed, rightSpeed, gripper]

#for arduino again, this is PWM to attain speed control
enablePin1 = board.get_pin('d:6:p')
enablePin2 = board.get_pin('d:7:p')

global gripped

def grip():
    if gripped:
        gripper.write(180)
    elif not gripped:
        gripper.write(0)
    else:
        print 'gripper failed lol'
    print 'gripper changed'

def setMotor1(j, k, speed):
	in1pin.write(j)
	in2pin.write(k)
	#elif
		#Kills motors if unintelligible request
		#in1pin.write(0)
		#in2pin.write(0)

	enablePin1.write(speed/255.0)
	#print(speed/255.0)
	
def setMotor2(j, k, speed):
    in3pin.write(j)
    in4pin.write(k)
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

# Settings for the Remote server
portListen = 9038

class PicoBorgHandler(SocketServer.BaseRequestHandler):
    # Function called when a new message has been received
    def handle(self):
        global isRunning
		
        request, socket = self.request          # Read who spoke to us and what they said
        request = request.upper()               # Convert command to upper case
        driveCommands = request.split(',')      # Separate the command into individual drives
        if len(driveCommands) == 1:  # Special commands
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

        elif len(driveCommands) == len(lOutputs): # Just driving as usual
            # For each drive we check the command
            for driveNo in range(len(driveCommands)):
                command = driveCommands[driveNo]
                print driveNo
                if command == 'ON':
                    lOutputs[driveNo] = 1
                elif command == 'OFF':
                    lOutputs[driveNo] = 0
                elif command == 'GRIP':
                    grip()
                elif command == 'X': # No command for this drive
                    pass
                else:
                    lOutputs[driveNo] = int(command)
                    print 'driveSpeed: %s' % command
            setMotor1(lOutputs[0],lOutputs[1],lOutputs[4])
            setMotor2(lOutputs[2],lOutputs[3],lOutputs[5])
        else:
            # Did not get the right number of drive commands
            print 'Command "%s" did not have %d parts!' % (request, len(lOutputs))

try:
    global isRunning
    # Start by turning all drives off
    MotorOff()
    raw_input('Press ENTER to continue')
    # Setup the UDP listener
    remoteKeyBorgServer = SocketServer.UDPServer(('', portListen), PicoBorgHandler)
    # Loop until terminated remotely
    isRunning = True
    while isRunning:
        remoteKeyBorgServer.handle_request()
    # Turn off the drives and release the GPIO pins
    print 'Finished'
    MotorOff()
    raw_input('Turn the motor power off now, press ENTER to continue')
    GPIO.cleanup()
except KeyboardInterrupt:
    # CTRL+C exit, turn off the drives and release the GPIO pins
    print 'Terminated'
    MotorOff()
    raw_input('Turn the motor power off now, press ENTER to continue')
    GPIO.cleanup()
