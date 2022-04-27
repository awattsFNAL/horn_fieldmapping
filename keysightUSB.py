import visa
import Adafruit_BBIO.GPIO as GPIO
import struct
import numpy as np
import time

# Keysight DSO-X 2014A scope

# Set up scope for external trigger, any other setup options needed
# Physically, BBB and scope share same external trigger (~1Hz)
# On first trigger received by BBB (blocking interrupt), start loop that waits for the next trigger
# Inside loop, on trigger (blocking interrupt), tell scope to save data to file (usb)
    
def getChannelData(ch_num):
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
    
    return time, voltage

# Initialize connection to scope
print "Connecting to scope."
rm = visa.ResourceManager('@py')
scope = rm.open_resource('USB0::2391::6040::MY54490470::INSTR')
print scope.query('*IDN?')

# Set up scope
print "Configuring scope"
scope.write(":WAVEFORM:FORMAT BYTE")
scope.write(":WAVeform:POINts:MODE NORMAL")
scope.write(":WAVeform:POINts 1000")

# Initalize trigger on BBB
trigger_pin = "P8_8"
GPIO.setup(trigger_pin, GPIO.IN)

# Wait for first trigger to start data capture loop, arm scope trigger
print "Waiting for initial trigger."
GPIO.wait_for_edge(trigger_pin, GPIO.RISING)
scope.write(':SINGLE')
GPIO.wait_for_edge(trigger_pin, GPIO.RISING)
time1, voltage1 = getChannelData('1')
time2, voltage2 = getChannelData('2')
time3, voltage3 = getChannelData('3')
time4, voltage4 = getChannelData('4')
print 'Data acquired, writing to file.'
with open('data.txt','w') as f:
    f.write('CH1_time \t CH1_voltage \t CH2_time \t CH2_voltage \t CH3_time \t CH3_voltage \t CH4_time \t CH4_voltage\n')
    for i in range(voltage1.size):
        f.write(str(time1[i])+'\t'+str(voltage1[i])+'\t'+str(time2[i])+'\t'+str(voltage2[i])+'\t'+str(time3[i])+'\t'+str(voltage3[i])+'\t'+str(time4[i])+'\t'+str(voltage4[i])+'\n')

#while True:
#    GPIO.wait_for_edge(trigger_pin, GPIO.RISING)
#    
#    scope.write(':SINGLE')

