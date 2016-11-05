#!/usr/bin/env python
# coding: Latin-1

# Load library functions we want
import socket
import time
import pygame

# Settings for the RemoteJoyBorg client
broadcastIP = '192.168.1.100'           # IP address to send to, 255 in one or more positions is a broadcast / wild-card
broadcastPort = 9038                    # What message number to send with
leftDrive = 0                           # Drive number for left motor
rightDrive = 2                          # Drive number for right motor
interval = 0.05                          # Time between updates in seconds, smaller responds faster but uses more processor time
regularUpdate = True                    # If True we send a command at a regular interval, if False we only send commands when keys are pressed or released
axisUpDown = 1                          # Joystick axis to read for up / down position
axisUpDownInverted = False              # Set this to True if up and down appear to be swapped
axisLeftRight = 0                       # Joystick axis to read for left / right position
axisLeftRightInverted = False           # Set this to True if left and right appear to be swapped

# Setup the connection for sending on
sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)       # Create the socket
sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)                        # Enable broadcasting (sending to many IPs based on wild-cards)
sender.bind(('0.0.0.0', 0))                                                         # Set the IP and port number to use locally, IP 0.0.0.0 means all connections and port 0 means assign a number for us (do not care)

# Setup pygame and key states
global hadEvent
global moveUp
global moveDown
global moveLeft
global moveRighte
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
        elif event.type == pygame.JOYAXISMOTION:
            # A joystick has been moved, read axis positions (-1 to +1)
            hadEvent = True
            upDown = joystick.get_axis(axisUpDown)
            leftRight = joystick.get_axis(axisLeftRight)
            # Invert any axes which are incorrect
            if axisUpDownInverted:
                upDown = -upDown
            if axisLeftRightInverted:
                leftRight = -leftRight
            # Determine Up / Down values
            if upDown > 0.1:
                moveUp = True
                moveDown = False
            elif upDown < -0.1:
                moveUp = False
                moveDown = True
            else:
                moveUp = False
                moveDown = False
            # Determine Left / Right values
            if leftRight < -0.1:
                moveLeft = True
                moveRight = False
            elif leftRight > 0.1:
                moveLeft = False
                moveRight = True
            else:
                moveLeft = False
                moveRight = False

try:
    print 'Press [ESC] to quit'
    # Loop indefinitely
    while True:
        # Get the currently pressed keys on the keyboard
        PygameHandler(pygame.event.get())
        if hadEvent or regularUpdate:
            # Keys have changed, generate the command list based on keys
            hadEvent = False
            driveCommands = ['X', 'X', 'X', 'X']                    # Default to do not change
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
                driveCommands[rightDrive] = 'OFF'
                driveCommands[rightDrive+1] = 'OFF'
            # Send the drive commands
            command = ''
            for driveCommand in driveCommands:
                command += driveCommand + ','
            command = command[:-1]                                  # Strip the trailing comma
            sender.sendto(command, (broadcastIP, broadcastPort))
        # Wait for the interval period
        time.sleep(interval)
    # Inform the server to stop
    sender.sendto('ALLOFF', (broadcastIP, broadcastPort))
except KeyboardInterrupt:
    # CTRL+C exit, inform the server to stop
    sender.sendto('ALLOFF', (broadcastIP, broadcastPort))
