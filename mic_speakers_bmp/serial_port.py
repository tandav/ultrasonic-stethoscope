'''
lengths are in bytes
'''

import collections
import numpy as np
import sys; sys.path.append('/Users/tandav/Documents/spaces/arduino'); import arduino
port = arduino.find_device()

header = b'\xd2\x02\x96I'

bmp_pressure_length    =   4 # float32 number
mic_length        = 512 # 256 uint16
mic_chunk_size         = mic_length // 2 # uint16 takes 2 bytes

is_tone_playing_length =   1 # uint8 (used like bool)
payload_length         = 2 * bmp_pressure_length + is_tone_playing_length + mic_length
packet_length          = len(header) + payload_length



n_good_packets = 0


def wait_header():
    deque = collections.deque(maxlen=len(header))

    while b''.join(deque) != header:
        deque.append(port.read())

    print('wait done', b''.join(deque), '==', header)


def read_packet_bytes():
    '''
    packet_length: packet length in bytes
    returns packet without header (bytes)
    '''

    global n_good_packets

    packet = port.read(packet_length)

    if packet.startswith(b'\xd2\x02\x96I'):
        n_good_packets += 1
        if n_good_packets % 4000 == 0:
            print(f'n_good_packets = {n_good_packets}')
        return packet[len(header):]
    else:
        print(f'wrong header {packet[:len(header)]} before: n_good_packets = {n_good_packets}')
        n_good_packets = 0
        # time.sleep(1)
        wait_header()
        return port.read(payload_length) # rest of packet


def read_packet():
    packet = read_packet_bytes()

    # parse data from bytes packet
    bmp0 = np.frombuffer(packet[ :4], dtype=np.float32)[0]
    bmp1 = np.frombuffer(packet[4:8], dtype=np.float32)[0]
    is_tone_playing = np.frombuffer(packet[8:9], dtype=np.uint8)[0]
    mic = np.frombuffer(packet[9:], dtype=np.uint16)

    return bmp0, bmp1, is_tone_playing, mic
