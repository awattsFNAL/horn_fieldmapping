import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.ADC as ADC
import time
import numpy as np
from scope_communication import *
from os import system

def move(dir_pin, step_pin, direction):
    npulses = 200
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
    ref = 1.8 # ADC reference voltage

    nreadings = 50
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
    
    return X, Y, Z, xsig, ysig, zsig
    
def readScopes(stripline_scope, field_scope,X_pos, Y_pos, Z_pos):
    # Define the number of data points to take
    npoints = 5
    point = 1

    stripline_times1 = []
    stripline_voltages1 = []
    stripline_times2 = []
    stripline_voltages2 = []
    stripline_times3 = []
    stripline_voltages3 = []
    stripline_times4 = []
    stripline_voltages4 = []

    Xfield_times = []
    Xfield_voltages = []
    Yfield_times = []
    Yfield_voltages = []
    Zfield_times = []
    Zfield_voltages = []

    while point != (npoints+1):
        # Wait for a horn trigger
        GPIO.wait_for_edge(trigger, GPIO.RISING)
        # Download the scope data (does this need a delay?)
        stripline_time1, stripline_voltage1 = acquire(stripline_scope_type, stripline_scope, 1)
        stripline_time2, stripline_voltage1 = acquire(stripline_scope_type, stripline_scope, 2)
        stripline_time3, stripline_voltage1 = acquire(stripline_scope_type, stripline_scope, 3)
        stripline_time4, stripline_voltage1 = acquire(stripline_scope_type, stripline_scope, 4)
        Xfield_time, Xfield_voltage = acquire(field_scope_type, field_scope, 1)
        Yfield_time, Yfield_voltage = acquire(field_scope_type, field_scope, 2)
        Zfield_time, Zfield_voltage = acquire(field_scope_type, field_scope, 3)
        
        stripline_times1.append(stripline_time1)
        stripline_voltages1.append(stripline_voltage1)
        stripline_times2.append(stripline_time2)
        stripline_voltages2.append(stripline_voltage2)
        stripline_times3.append(stripline_time3)
        stripline_voltages3.append(stripline_voltage3)
        stripline_times4.append(stripline_time4)
        stripline_voltages4.append(stripline_voltage4)
        Xfield_times.append(Xfield_time)
        Xfield_voltages.append(Xfield_voltage)
        Yfield_times.append(Xfield_time)
        Yfield_voltages.append(Xfield_voltage)
        Zfield_times.append(Xfield_time)
        Zfield_voltages.append(Xfield_voltage)
        
        # Increment the point count
        point = point + 1    
        
        print 'Data point %i acquired.'%(point)
    
    # Get the position of the stage
    print 'Acquiring stage position.'_
    X, Y, Z, xsig, ysig, zsig readPosition(X_pos, Y_pos, Z_pos)
    
    filename = 'X=%.2f_Y=%.2f_Z=%.2f'%(X_pos, Y_pos, Z_pos)
    print 'Writing data to file.'
    with open(filename, 'w') as f:
        f.write('X = %.4f +/- %.4f \t Y = %.4f +/- %.4f \t Z = %.4f +/- %.4f \n'%(X, xsig, Y, ysig, Z, zsig))
        f.write('\n')
        for i in range(len(stripline_times1)):
            # Need to add a conversion to mm and Tesla here
            f.write('Strip1_t, Strip1_V \t Strip2_t, Strip2_V \t Strip3_t, Strip3_V \t Strip4_t, Strip4_V \t Xfield_t, Xfield_V \ Yfield_t, Yfield_V \t Zfield_t, Zfield_V \n'%(stripline_times1[i], stripline_voltages1[i], stripline_times2[i], stripline_voltages2[i], stripline_times3[i], stripline_voltages3[i], stripline_times4[i], stripline_voltages4[i], Xfield_t[i], Xfield_V[i], Yfield_t[i], Yfield_V[i], Zfield_t[i], Zfield_V[i])
    
    print 'Data acquisition complete'
    print('\nX: %.4f +/- %.4f,\nY: %.4f +/- %.4f,\nZ: %.4f +/- %.4f\n'%(X,xsig,Y,ysig,Z,zsig))
    
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

trigger = 'P8_7'
###

### Setup motor pulse pins ###
GPIO.setup(MotorX_dir, GPIO.OUT)
GPIO.setup(MotorX_step, GPIO.OUT)
GPIO.setup(MotorY_dir, GPIO.OUT)
GPIO.setup(MotorY_step, GPIO.OUT)
GPIO.setup(MotorZ_dir, GPIO.OUT)
GPIO.setup(MotorZ_step, GPIO.OUT)
###

### Setup trigger input pin ###
GPIO.setup(trigger, GPIO.IN)
###


### Setup ADC ###
ADC.setup()
###

### Setup oscilloscopes ###
stripline_scope_IP = '192.168.1.2'
stripline_scope_type = 'Agilent'

field_scope_IP = '192.168.1.3'
field_scope_type = 'Agilent'

# Setup BBB ethernet connection
print 'Setting up BeagleBone ethernet connection.'
system('sudo ifconfig eth0 192.168.1.1 netmask 255.255.248.0')

# Setup stripline scope
print 'Initializing stripline scope.'
stripline_scope = initialize(stripline_scope_type, stripline_scope_IP)

# Setup field scope
print 'Initializing magnetic field scope.'
field_scope = initialize(field_scope_type, field_scope_IP)

###


################## MAIN LOOP ######################

print('Starting positions:')
readPosition(X_pos, Y_pos, Z_pos)
while 1:
    print('Press: [L]eft, [R]ight, [U]p, [D]own, [F]orward, [B]ack, or [A]cquire data, then <Enter>. Press CTRL+C to exit.')
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
    elif variable == 'a':
        readScopes(stripline_scope, field_scope,X_pos, Y_pos, Z_pos)
    else:
        print('Invalid command.')
        print('Press: [L]eft, [R]ight, [U]p, [D]own, [F]orward, [B]ack, or [A]cquire data, then <Enter>. Press CTRL+C to exit.')
