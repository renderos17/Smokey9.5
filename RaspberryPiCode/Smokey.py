import RPi.GPIO as GPIO
from pyfirmata import Arduino, ArduinoMega, util
import SocketServer
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
lDrives = [in1pin, in2pin, in3pin, in4pin]

#for arduino again, this is PWM to attain speed control
enablePin1 = board.get_pin('d:6:p')
enablePin2 = board.get_pin('d:7:p')

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

# Settings for the Remote server
portListen = 9038

class PicoBorgHandler(SocketServer.BaseRequestHandler):
    # Function called when a new message has been received
    def handle(self):
        global isRunning
		
        request, socket = self.request          # Read who spoke to us and what they said
        request = request.upper()               # Convert command to upper case
        driveCommands = request.split(',')      # Separate the command into individual drives
        print '2-pac-et'
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
                    print 'on my bois'
                elif command == 'OFF':
                    # Set drive off
                    lDrives[driveNo].write(0)
                    print 'off my dudes'
                elif command == 'X':
                    # No command for this drive
                    print 'wot'
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
