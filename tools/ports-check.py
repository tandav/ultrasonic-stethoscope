import serial # TODO: try del
import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())

# print(ports)

for p in ports:
    print(p.description)
