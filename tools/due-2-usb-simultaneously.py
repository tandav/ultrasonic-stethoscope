import time
import serial # TODO: try del
import serial.tools.list_ports
import sys

# def find_device_and_return_port():
#     for i in range(61):
#         ports = list(serial.tools.list_ports.comports())
#         for port in ports:
#             if 'Arduino' in port.description or \
#                'Устройство с последовательным интерфейсом USB' in port.description or \
#                'USB Serial Device' in port.description: 
#             # if ('Устройство с последовательным интерфейсом USB') in port.description: 
#                 # try / except
#                 ser = serial.Serial(port.device)
#                 print('device connected')
#                 break
#         else:
#             if i == 60:
#                 print('\nDevice not found. Check the connection.')
#                 sys.exit()
#             sys.stdout.write('\rsearching device' + '.'*i + ' ')
#             sys.stdout.flush()
#             time.sleep(0.05)
#             continue  # executed if the loop ended normally (no break)
#         break  # executed if 'continue' was skipped (break)
#     return ser


# port = find_device_and_return_port() # serial port handle



ports = list(serial.tools.list_ports.comports())
for port in ports:
    # print(port.description)
    if port.description == 'Arduino Due Prog_ Port':
        programming_port = serial.Serial(port.device)
    if port.description == 'Arduino Due':
        native_port = serial.Serial(port.device)

# while(True):
    # pass
    # x = programming_port.readline()
    # print(x, time.time())

