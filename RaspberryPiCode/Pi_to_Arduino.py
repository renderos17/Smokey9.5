from pyfirmata import Arduino, util
import time

#This code will talk to an Arduino unit loaded with the StandardFirmata code and operate 2 pins as a test.
#To be implemented in RDE.py soon.

board = Arduino('/dev/ttyACM0')
led_pin1 = board.get_pin('d:10:o')
led_pin2 = board.get_pin('d:11:o')

while True:
    led_pin1.write(1)
    led_pin2.write(0)
    time.sleep(0.5)
    led_pin1.write(0)
    led_pin2.write(1)
    time.sleep(0.5)
