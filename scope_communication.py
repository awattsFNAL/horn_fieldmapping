import pyvisa as visa
import numpy as np
import struct
import sys

# Change prints to logger outputs

def initialize(scope_type, IP_address):
    ''' Initalize and connect to oscilliscope. Supported scope types are Tektronix and Agilent,
    requiring slightly different commands for each.'''

    print("Connecting to {} scope @ {}".format(scope_type, IP_address))
    rm = visa.ResourceManager('@py')
    try:
        if scope_type is 'Agilent':
            # Initialize connection to scope
            scope = rm.open_resource('TCPIP0::%s::inst0::INSTR'%(IP_address))
            print(scope.query('*IDN?'))
            # Set up scope
            print("Connection successful. Configuring scope.")
            scope.write(":WAVEFORM:FORMAT BYTE")
            scope.write(":WAVeform:POINts:MODE NORMAL")
            scope.write(":WAVeform:POINts 100")
            #scope.write(":TRIGger:MODE EDGE")
            #scope.write(":TRIGger:SOURce EXTernal")
            #scope.write(":TRIGger:LEVel 0.5")
            print("Configuration complete.")
            return scope
        elif scope_type is 'Tektronix':
            scope = rm.open_resource('TCPIP0::%s::inst0::INSTR'%(IP_address))
            print(scope.query('*IDN?'))
            return scope
    except Exception as e:
        print(e)

def acquire(scope_type, scope, ch_num):
    '''Acquire data from a given scope's channel, returning a time and voltage array for that trigger.'''
    if scope_type is 'Agilent':
        #scope.write(':WAVEFORM:SOURCE CHANNEL'+str(ch_num))
        #x_increment = float(scope.query(":WAVeform:XINCrement?"))
        #x_origin = float(scope.query(":WAVeform:XORigin?"))
        #y_increment = float(scope.query(":WAVeform:YINCrement?"))
        #y_origin = float(scope.query(":WAVeform:YORigin?"))
        #y_reference = float(scope.query(":WAVeform:YREFerence?"))
        #sData = scope.query_binary_values(":WAVeform:DATA?", datatype='s')[0]
        #values = np.array(struct.unpack("%dB" % len(sData), sData))
        #time = np.linspace(x_origin, values.size*x_increment-1, values.size)*-1.0
        #voltage = ((values - y_reference) * y_increment) + y_origin
        #return time, voltage
	
	print "Getting data from Channel "+str(ch_num)
        scope.write(':WAVEFORM:SOURCE CHANNEL'+str(ch_num))
    
        x_increment = float(scope.query(":WAVeform:XINCrement?"))
        x_origin = float(scope.query(":WAVeform:XORigin?"))
        y_increment = float(scope.query(":WAVeform:YINCrement?"))
        y_origin = float(scope.query(":WAVeform:YORigin?"))
        y_reference = float(scope.query(":WAVeform:YREFerence?"))

        sData = scope.query_binary_values(":WAVeform:DATA?", datatype='s')[0]
        values = np.array(struct.unpack("%dB" % len(sData), sData))
        time = np.linspace(x_origin, values.size*x_increment-1, values.size)*-1.0
        voltage = ((values - y_reference) * y_increment) + y_origin
    
	
    elif scope_type is 'Tektronix':
        scope.write('DATA:SOU CH'+str(ch_num))
        scope.write('DATA:ENC RPB')
        ymult = float(scope.query('WFMPRE:YMULT?'))
        yzero = float(scope.query('WFMPRE:YZERO?'))
        yoff = float(scope.query('WFMPRE:YOFF?'))
        xincr = float(scope.query('WFMPRE:XINCR?'))
        scope.write('CURVE?')
        data = scope.read_raw()
        headerlen = 2+int(data[1])
        header = data[:headerlen]
        ADC_wave = data[headerlen:-1]
        ADC_wave = np.array(struct.unpack('%sB' % len(ADC_wave),ADC_wave))
        voltage = (ADC_wave-yoff)*ymult+yzero
        time = np.arange(0,xincr*len(voltage),xincr)
	
    return time, voltage
