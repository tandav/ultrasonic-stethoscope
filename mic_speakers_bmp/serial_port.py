import collections
import sys; sys.path.append('/Users/tandav/Documents/spaces/arduino'); import arduino
port = arduino.find_device()

header = b'\xd2\x02\x96I'
# payload_length = 4 + 4 + 1 + 512
payload_length = 4 + 4 + 1
packet_length = len(header) + payload_length

n_good_packets = 0



def wait_header():
    deque = collections.deque(maxlen=len(header))

    while b''.join(deque) != header:
        deque.append(port.read())

    print('done', b''.join(deque), '==', header)




def read_packet():
    '''
    packet_length: packet length in bytes
    returns packet without header
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
