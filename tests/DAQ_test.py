import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt
import struct
import sys

def acquire(scope_IP, ch_num):
    '''Acquire data from a given scope's channel, returning a time and voltage array for that trigger.'''
    try:
        rm = visa.ResourceManager('@py')
        scope = rm.open_resource('TCPIP0::%s::inst0::INSTR'%(scope_IP))
        print(scope.query('*IDN?'))

        # Clear the status data structures, the device-defined error queue, and the Request-for-OPC flag
        scope.write('*CLS')

        scope.write(":ACQuire:TYPE NORMal")
        scope.write(":TIMebase:MODE MAIN")
        # Make sure WORD and BYTE data is transeferred as signed ints and lease significant bit first
        scope.write(':WAVeform:UNSigned OFF')
        scope.write(':WAVeform:BYTeorder LSBFirst') # MSBF is default, must be overridden for WORD to work
        scope.write(":WAVeform:SOURce CHANnel{}".format(ch_num))
        scope.write(":WAVeform:FORMat WORD")
        scope.write(":WAVeform:POINts 100")

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

    except Exception as e:
        print(e)

scope_IP = "169.254.189.129"
ch_num = "1"

t1, v1 = acquire(scope_IP, 1)
#t2, v2 = acquire(scope_IP, 2)
#t3, v3 = acquire(scope_IP, 3)
#t4, v4 = acquire(scope_IP, 4)

plt.plot(t1, v1)
#plt.plot(t2, v2)
#plt.plot(t3, v3)
#plt.plot(t4, v4)
plt.grid()
plt.ylim()
plt.show()