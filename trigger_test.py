import Adafruit_BBIO.GPIO as GPIO

trigger = 'P8_7'

GPIO.setup(trigger, GPIO.IN)

while 1:
    GPIO.wait_for_edge(trigger, GPIO.RISING)
    print 'Trigger.'
