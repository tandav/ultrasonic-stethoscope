

import socket
import struct
from math import sin, pi

TCP_IP = '192.168.137.1'

TCP_PORT = 5005
BUFFER_SIZE = 1024
# MESSAGE = "str1"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))


s.send((100).to_bytes(4, byteorder='little'))


for i in range(100):
	m = int(10000 * sin(pi * i / 3))
	s.send(struct.pack("<i", m))

	


# MESSAGE = "Testmessage"



n = int.from_bytes(s.recv(4), byteorder='little')
for i in range(n):
	data = s.recv(4)
	data = struct.unpack('f', data)
	print("received data:", data)


# data = s.recv(BUFFER_SIZE)
s.close()

# data = int.from_bytes(data, byteorder='little')
# data = struct.unpack('f', data)
# print("received data:", data)

# n= 254
# print n.to_bytes(n.bit_length(), 'big')