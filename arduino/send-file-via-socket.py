import numpy as np
import sys, socket
import h5py


# Collect Write to File and Compress data
adc_samples = np.array([], dtype=np.float32)
with h5py.File('to_cuda.h5', 'w') as f:
    adc_samples = np.arange(8)
    f.create_dataset('adc_samples', data=adc_samples, compression='lzf')

# Send data to CUDA server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# s.connect((TCP_IP, TCP_PORT))
s.connect(('192.168.1.37', 5005))
blocksize = 8192 # or some other size packet you want to transmit. Powers of 2 are good.
# with open('to_cuda.h5', 'rb') as f:
with open('spring.png', 'rb') as f:
    packet = f.read(blocksize)
    print('start sending data to CUDA server...')
    i = 0
    while packet: # send until the end of file
        s.send(packet)
        packet = f.read(blocksize)
        i += 1
        # if i % 1000 == 0:
        # if i < 100:
            # print(i, packet)
            # print('sent', i, 'K blocks')
    print('send data: success')

# s.close()
