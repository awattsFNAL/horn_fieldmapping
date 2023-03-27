import pyvisa as visa
import numpy as np
import sys
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.ADC as ADC
import time

# Change prints to logger outputs
# Move parameters to a config file
# Convert DAQ data to dictionary?

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
	
def read_position(X_pin, Y_pin, Z_pin):
    ref = 1.8 # ADC reference voltage

    nreadings = 50
    reading = 1
    
    x_readings = np.zeros(nreadings)
    y_readings = np.zeros(nreadings)
    z_readings = np.zeros(nreadings)
    
    while reading != (nreadings+1):
        x_readings[reading-1] = ref*float(ADC.read(X_pin))
        y_readings[reading-1] = ref*float(ADC.read(Y_pin))
        z_readings[reading-1] = ref*float(ADC.read(Z_pin))
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

def initialize_scope(IP_address):
    ''' Initalize and connect to oscilliscope.'''

    print("Connecting to scope @ {}".format(IP_address))
    rm = visa.ResourceManager('@py')
    try:
        # Initialize connection to scope
        scope = rm.open_resource('TCPIP0::%s::inst0::INSTR'%(IP_address))
        print(scope.query('*IDN?'))
        if scope:
            print("Connection successful. Configuring scope.")

        # Clear the status data structures, the device-defined error queue, and the Request-for-OPC flag
        scope.write('*CLS')

        # Set up scope parameters
        scope.write(":ACQuire:TYPE NORMal")
        scope.write(":TIMebase:MODE MAIN")
        # Make sure WORD and BYTE data is transeferred as signed ints and lease significant bit first
        scope.write(':WAVeform:UNSigned OFF')
        scope.write(':WAVeform:BYTeorder LSBFirst') # MSBF is default, must be overridden for WORD to work
        scope.write(":WAVeform:SOURce CHANnel{}".format(ch_num))
        scope.write(":WAVeform:FORMat WORD")
        scope.write(":WAVeform:POINts 100")
        # External triggering
        #scope.write(":TRIGger:MODE EDGE")
        #scope.write(":TRIGger:SOURce EXTernal")
        #scope.write(":TRIGger:LEVel 0.5")
        print("Configuration complete.")
        return scope

    except Exception as e:
        print(e)

def acquire_channel(scope, ch_num):
    '''Acquire data from a given scope's channel, returning a time and voltage array for that trigger.'''
	
	print("Getting data from Channel "+str(ch_num))

    scope.write(":SINGle")
    preamble = scope.query(':WAVeform:PREamble?').split(',')
    values = scope.query_binary_values(':WAVeform:DATA?', datatype='h', container=np.array)

    num_samples = int(preamble[2])

    x_increment, x_origin, x_reference = float(preamble[4]), float(preamble[5]), float(preamble[6])
    time = np.array([(np.arange(num_samples)-x_reference)*x_increment + x_origin]) # compute x-values
    time = time.T # make x values vertical

    y_increment, y_origin, y_reference = float(preamble[7]), float(preamble[8]), float(preamble[9])
    voltage = (values-y_reference)*y_increment + y_origin

    return time, voltage

def full_DAQ(field_scope, stripline_scope):

    field_t1, field_v1 = acquire_channel(field_scope, 1)
    field_t2, field_v2 = acquire_channel(field_scope, 2)
    field_t3, field_v3 = acquire_channel(field_scope, 3)

    stripline_t1, stripline_v1 = acquire_channel(stripline_scope, 1)
    stripline_t2, stripline_v2 = acquire_channel(stripline_scope, 2)
    stripline_t3, stripline_v3 = acquire_channel(stripline_scope, 3)
    stripline_t4, stripline_v4 = acquire_channel(stripline_scope, 4)

    X, Y, Z, xsig, ysig, zsig = read_position(X_pin, Y_pin, Z_pin)
    
def write_to_file(data_dict):
    filename = 'X=%.2f_Y=%.2f_Z=%.2f'%(X_pos, Y_pos, Z_pos)
    print("Writing data to file.")
    with open(filename, 'w') as f:
        f.write('X = %.4f +/- %.4f \t Y = %.4f +/- %.4f \t Z = %.4f +/- %.4f \n'%(X, xsig, Y, ysig, Z, zsig))
        f.write('\n')
        for i in range(len(stripline_times1)):
            # Need to add a conversion to mm and Tesla here
            f.write('Strip1_t, Strip1_V \t Strip2_t, Strip2_V \t Strip3_t, Strip3_V \t Strip4_t, Strip4_V \t Xfield_t, Xfield_V \ Yfield_t, Yfield_V \t Zfield_t, Zfield_V \n'%(stripline_times1[i], stripline_voltages1[i], stripline_times2[i], stripline_voltages2[i], stripline_times3[i], stripline_voltages3[i], stripline_times4[i], stripline_voltages4[i], Xfield_t[i], Xfield_V[i], Yfield_t[i], Yfield_V[i], Zfield_t[i], Zfield_V[i])
    
    print 'Data acquisition complete'
    print('\nX: %.4f +/- %.4f,\nY: %.4f +/- %.4f,\nZ: %.4f +/- %.4f\n'%(X,xsig,Y,ysig,Z,zsig))