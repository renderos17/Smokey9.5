import socket
import time
import pygame

#this code manages the DriverStation for the robot.
#it also handles all controller data for direct interpretation by the bot
#Created by Alexis Renderos


# Settings for the RemoteJoyBorg client
broadcastIP = '192.168.1.100'           # IP address to send to, 255 in one or more positions is a broadcast / wild-card
broadcastPort = 9038                    # What message number to send with
leftDrive = 0                           # Drive number for left motor in terms of output arr
rightDrive = 2                          # Drive number for right motor in terms of output arr
interval = 0.05                         # Time between updates in seconds, smaller responds faster but uses more processor time
regularUpdate = True                    # If True we send a command at a regular interval, if False we only send commands when keys are pressed or released

# Settings for the Controller Map
gripButton = 2 # the "A" button
driveAxisX = 1
driveAxisY = 0
driveAxisXinverted = False
driveAxisYinverted = False
deadX = 0.1 # Modifies deadzone on Left/Right axis of travel
deadY = 0.1 # Modifies deadzone on Up/Down axis of travel


# Setup the connection for sending on
sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)       # Create the socket
sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)                        # Enable broadcasting (sending to many IPs based on wild-cards)
sender.bind(('0.0.0.0', 0))                                                         # Set the IP and port number to use locally, IP 0.0.0.0 means all connections and port 0 means assign a number for us (do not care)

# Setup pygame and key states
global hadEvent
global moveUp
global moveDown
global moveLeft
global moveRight
global moveQuit

hadEvent = True
moveUp = False
moveDown = False
moveLeft = False
moveRight = False
moveQuit = False

pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()
screen = pygame.display.set_mode([480,320])
pygame.display.set_caption("Smokey9.5 Driver Station - Press [ESC] to quit")

def mapScalar(val, curLow, curHigh, toLow, toHigh):
    return (val - curLow) * (toHigh - toLow) / (curHigh - curLow) + toLow

def getArcadeLeft(xScala, yScala):
    return yScala + xScala

def getArcadeRight(xScala, yScala):
    return yScala - xScala

# Function to handle pygame events
def PygameHandler(events):
    # Variables accessible outside this function
    global hadEvent
    global moveUp
    global moveDown
    global moveLeft
    global moveRight
    global moveQuit
    # Handle each event individually
    for event in events:
        if event.type == pygame.QUIT:
            # User exit
            hadEvent = True
            moveQuit = True
        elif event.type == pygame.KEYDOWN:
            # A key has been pressed, see if it is one we want
            hadEvent = True
            if event.key == pygame.K_ESCAPE:
                moveQuit = True
        elif event.type == pygame.JOYBUTTONDOWN:
            # A button has been pressed, lets process it further.
            gripAct = joystick.get_axis(gripButton)
        elif event.type == pygame.JOYAXISMOTION:
            # A joystick has been moved, read axis positions (-1 to +1)
            hadEvent = True
            upDown = joystick.get_axis(driveAxisY)
            leftRight = joystick.get_axis(driveAxisX)
            # Invert any axes which are incorrect
            if driveAxisYinverted:
                upDown = -upDown
            if driveAxisXinverted:
                leftRight = -leftRight
            # Determine Up / Down values
            if upDown > deadX:
                moveUp = True
                moveDown = False
                upDown = mapScalar(upDown, -1, 1, -255, 255)
            elif upDown < -deadX:
                moveUp = False
                moveDown = True
                upDown = mapScalar(upDown, -1, 1, -255, 255)
            else:
                moveUp = False
                moveDown = False
                upDown = 0
            # Determine Left / Right values
            if leftRight < -deadY:
                moveLeft = True
                moveRight = False
                leftRight = mapScalar(leftRight, -1, 1, -255, 255)
            elif leftRight > deadY:
                moveLeft = False
                moveRight = True
                leftRight = mapScalar(leftRight, -1, 1, -255, 255)
            else:
                moveLeft = False
                moveRight = False
                leftRight = 0
try:
    print 'Press [ESC] to quit'
    # Loop indefinitely
    while True:
        # Get the currently pressed keys on the keyboard
        PygameHandler(pygame.event.get())
        if hadEvent or regularUpdate:
            # Keys have changed, generate the command list based on keys
            hadEvent = False
            driveCommands = ['X', 'X', 'X', 'X', 'X', 'X', 'X']
            # [DirectionL, DirectionL, DirectionR, DirectionR, SpeedL, SpeedR, GRIP]
            scala = [getArcadeLeft(leftRight,upDown),getArcadeRight(leftRight,upDown)] # Order is LEFT, RIGHT 
            driveCommands[rightDrive+2] = scala[0]
            driveCommands[rightDrive+3] = scala[1]
            if moveQuit:
                break
            elif moveLeft:
                driveCommands[leftDrive] = 'OFF'
                driveCommands[leftDrive+1] = 'ON'         
                driveCommands[rightDrive] = 'ON'
                driveCommands[rightDrive+1] = 'OFF'
            elif moveRight:
                driveCommands[leftDrive] = 'ON'
                driveCommands[leftDrive+1] = 'OFF'
                driveCommands[rightDrive] = 'OFF'
                driveCommands[rightDrive+1] = 'ON'
            elif moveUp:
                driveCommands[leftDrive] = 'ON'
                driveCommands[leftDrive+1] = 'OFF'
                driveCommands[rightDrive] = 'ON'
                driveCommands[rightDrive+1] = 'OFF'
            elif moveDown:
                driveCommands[leftDrive] = 'OFF'
                driveCommands[leftDrive+1] = 'ON'
                driveCommands[rightDrive] = 'OFF'
                driveCommands[rightDrive+1] = 'ON'
            else:
                # None of our expected keys, stop
                driveCommands[leftDrive] = 'OFF'
                driveCommands[leftDrive+1] = 'OFF'
                driveCommands[rightDrive+2] = 0
                driveCommands[rightDrive] = 'OFF'
                driveCommands[rightDrive+1] = 'OFF'
                driveCommands[rightDrive+3] = 0
            if gripAct == 1:
                driveCommands[rightDrive+4] = 'GRIP'

            # Send the drive commands
            command = ''
            for driveCommand in driveCommands:
                command += driveCommand + ','
            command = command[:-1] # Strip the trailing comma
            sender.sendto(command, (broadcastIP, broadcastPort))
        # Wait for the interval period
        time.sleep(interval)
    # Inform the server to stop
    sender.sendto('ALLOFF', (broadcastIP, broadcastPort))
except KeyboardInterrupt:
    # CTRL+C exit, inform the server to stop
    sender.sendto('ALLOFF', (broadcastIP, broadcastPort))
