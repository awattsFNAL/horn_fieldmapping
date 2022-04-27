import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.ADC as ADC
import time
import numpy as np

'''
Test motors using keyboard keys for manual movement.
'''

### Setup GPIO ###

MotorX_dir = 'P8_10'
MotorX_step = 'P8_8'
MotorY_dir = 'P8_14'
MotorY_step = 'P8_12'
MotorZ_dir = 'P8_18'
MotorZ_step = 'P8_16'

X_pos = 'P9_40'
Y_pos = 'P9_38'
Z_pos = 'P9_36'

#trigger = 'P8_7'


### Setup motor pulse pins ###
GPIO.setup(MotorX_dir, GPIO.OUT)
GPIO.setup(MotorX_step, GPIO.OUT)
GPIO.setup(MotorY_dir, GPIO.OUT)
GPIO.setup(MotorY_step, GPIO.OUT)
GPIO.setup(MotorZ_dir, GPIO.OUT)
GPIO.setup(MotorZ_step, GPIO.OUT)
###

### Setup trigger input pin ###
#GPIO.setup(trigger, GPIO.IN)
###


### Setup ADC ###
ADC.setup()
###


def move(dir_pin, step_pin, direction):
    npulses = 2000
    pulse = 1
    if direction == 1:
        GPIO.output(dir_pin, GPIO.HIGH)
    elif direction == 0:
        GPIO.output(dir_pin, GPIO.LOW)
	
    while pulse != (npulses+1):
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(0.0005)
        GPIO.output(step_pin, GPIO.LOW)
        pulse = pulse+1
	time.sleep(0.0005)
	
    GPIO.output(dir_pin, GPIO.LOW)
	
def readPosition(X_pos, Y_pos, Z_pos):
	
    ref = 1.8

    nreadings = 100
    reading = 1
    
    x_readings = np.zeros(nreadings)
    y_readings = np.zeros(nreadings)
    z_readings = np.zeros(nreadings)
    
    while reading != (nreadings+1):
        x_readings[reading-1] = ref*float(ADC.read(X_pos))
        y_readings[reading-1] = ref*float(ADC.read(Y_pos))
        z_readings[reading-1] = ref*float(ADC.read(Z_pos))
	reading = reading + 1
	time.sleep(0.001)
	
    X = np.mean(x_readings)
    Y = np.mean(y_readings)
    Z = np.mean(z_readings)
    
    xsig = np.std(x_readings)
    ysig = np.std(y_readings)
    zsig = np.std(z_readings)
    
    print('\nX: %.4f +/- %.4f,\nY: %.4f +/- %.4f,\nZ: %.4f +/- %.4f\n'%(X,xsig,Y,ysig,Z,zsig))

print('Starting positions:')
readPosition(X_pos, Y_pos, Z_pos)
while 1:
    #readPosition(X_pos, Y_pos, Z_pos)
    #time.sleep(2.0)
    print('Press: [L]eft, [R]ight, [U]p, [D]own, [F]orward, or [B]ack, then <Enter>. Press CTRL+C to exit.')
    variable = str(raw_input())
    if variable == 'f':
        print("Moving forward")
        move(MotorZ_dir, MotorZ_step, 0)
        readPosition(X_pos, Y_pos, Z_pos)
    elif variable == 'b':
        print("Moving backward")
        move(MotorZ_dir, MotorZ_step, 1)
        readPosition(X_pos, Y_pos, Z_pos)
    elif variable == 'r':
        print("Moving right")
        move(MotorX_dir, MotorX_step, 1)
        readPosition(X_pos, Y_pos, Z_pos)
    elif variable == 'l':
        print("Moving left")
        move(MotorX_dir, MotorX_step, 0)
        readPosition(X_pos, Y_pos, Z_pos)
    elif variable == 'u':
        print("Moving up")
        move(MotorY_dir, MotorY_step, 1)
        readPosition(X_pos, Y_pos, Z_pos)
    elif variable == 'd':
        print("Moving down")
        move(MotorY_dir, MotorY_step, 0)
        readPosition(X_pos, Y_pos, Z_pos)
    else:
        print('Invalid command.')
        print('Press: [L]eft, [R]ight, [U]p, [D]own, [F]orward, or [B]ack, then <Enter>. Press CTRL+C to exit.')
