import numpy as np
from time import time, sleep
import serial

def beep(seconds, f=440):
    bs = 2**12 # buffer size
    buffer = np.zeros(bs)
    
    sample = 0
    start = time()
    while time() - start < seconds:
        buffer[sample] = np.sin(2 * np.pi * f * time())
        sample += 1
    stop = time()
    sps  = sample / (stop - start)
    return start, stop, sps




def find_device_and_return_port(self):
    for i in range(61):
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            if 'Arduino' in port.description or \
               'Устройство с последовательным интерфейсом USB' in port.description or \
               'USB Serial Device' in port.description: 
            # if ('Устройство с последовательным интерфейсом USB') in port.description: 
                # try / except
                ser = serial.Serial(port.device)
                print('device connected')
                break
        else:
            if i == 60:
                print('\nDevice not found. Check the connection.')
                sys.exit()
            sys.stdout.write('\rsearching device' + '.'*i + ' ')
            sys.stdout.flush()
            time.sleep(0.05)
            continue  # executed if the loop ended normally (no break)
        break  # executed if 'continue' was skipped (break)
    return ser

arduino = find_device_and_return_port()
arduino.write('some message to arduino')



def arduino_dac_beep():
    '''to do'''
    pass


# 10 beeps
for i in range(10):
    start, stop, sps = beep(0.0001)
    print('BEEP')
    print('start:\t', start)
    print('stop:\t',  stop)
    print('sps:\t',   sps)
    print('----------------------------------------------------------------')
    sleep(0.001)

'''
laptop > events, record start time > serial bus > arduino > dca > record stop time>

arduino > dac > 
'''


# print(len(buffer[buffer != 0]))

'''
----------------------------------------------------------------
import pyaudio

p = pyaudio.PyAudio()

volume = 0.5     # range [0.0, 1.0]
fs = 44100       # sampling rate, Hz, must be integer
duration = 8.0   # in seconds, may be float
f = 440.0        # sine frequency, Hz, may be float

# generate samples, note conversion to float32 array
samples = (np.sin(2 * np.pi * np.arange(fs * duration) * f / fs)).astype(np.float32)

# for paFloat32 sample values must be in range [-1.0, 1.0]
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=fs,
                output=True)

# play. May repeat with different volume values (if done interactively) 
stream.write(volume*samples)

stream.stop_stream()
stream.close()
p.terminate()
'''
