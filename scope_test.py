from scope_communication import *
import numpy as np
from os import system
import Adafruit_BBIO.GPIO as GPIO

# Define and setup the horn trigger pin
trigger = 'P8_7'
GPIO.setup(trigger, GPIO.IN)

stripline_scope_IP = '192.168.1.2'
stripline_scope_type = 'Agilent'

# Setup BBB ethernet connection
print 'Setting up BeagleBone ethernet connection.'
system('sudo ifconfig eth0 192.168.1.1 netmask 255.255.248.0')

# Setup stripline scope
print 'Initializing stripline scope.'
stripline_scope = initialize(stripline_scope_type, stripline_scope_IP)


# Define the number of data points to take
npoints = 5
point = 1

time_data = []
voltage_data = []

while point != (npoints+1):
    # Wait for a horn trigger
    GPIO.wait_for_edge(trigger, GPIO.RISING)
    # Download the scope data (does this need a delay?)
    time, voltage = acquire(stripline_scope_type, stripline_scope, 1)
    print 'Data point %i acquired.'%(point)
    time_data.append(time)
    voltage_data.append(voltage)
    
    # Increment the point count
    point = point + 1    
print 'Data acquisition complete'


# Print out data to check it
for n in range(len(time_data)):
    for i in range(len(time)):
        print '%i \t %f \t %f'%(n+1, time_data[n][i], voltage_data[n][i])
