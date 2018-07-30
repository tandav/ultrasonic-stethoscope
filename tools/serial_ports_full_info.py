import serial.tools.list_ports


ports = list(serial.tools.list_ports.comports())


for p in ports:
    print(
        'p.apply_usb_info' , p.apply_usb_info , '\n',
        'p.hwid'           , p.hwid           , '\n',
        'p.manufacturer'   , p.manufacturer   , '\n',
        'p.product'        , p.product        , '\n',
        'p.usb_info'       , p.usb_info       , '\n',
        'p.description'    , p.description    , '\n',
        'p.interface'      , p.interface      , '\n',
        'p.name'           , p.name           , '\n',
        'p.serial_number'  , p.serial_number  , '\n',
        'p.vid'            , p.vid            , '\n',
        'p.device'         , p.device         , '\n',     
        'p.location'       , p.location       , '\n',
        'p.pid'            , p.pid            , '\n',
        'p.usb_description', p.usb_description, '\n',
    )
    print('===========')


'''
p.apply_usb_info <bound method ListPortInfo.apply_usb_info of <serial.tools.list_ports_common.ListPortInfo object at 0x10db16748>> 
p.hwid n/a 
p.manufacturer None 
p.product None 
p.usb_info <bound method ListPortInfo.usb_info of <serial.tools.list_ports_common.ListPortInfo object at 0x10db16748>> 
p.description n/a 
p.interface None 
p.name None 
p.serial_number None 
p.vid None 
p.device /dev/cu.Bluetooth-Incoming-Port 
p.location None 
p.pid None 
p.usb_description <bound method ListPortInfo.usb_description of <serial.tools.list_ports_common.ListPortInfo object at 0x10db16748>> 

===========
p.apply_usb_info <bound method ListPortInfo.apply_usb_info of <serial.tools.list_ports_common.ListPortInfo object at 0x10db16780>> 
p.hwid USB VID:PID=2A03:003D SER=855313034313519121D0 LOCATION=20-1 
p.manufacturer Arduino (www.arduino.org) 
p.product Arduino Due Prog_ Port 
p.usb_info <bound method ListPortInfo.usb_info of <serial.tools.list_ports_common.ListPortInfo object at 0x10db16780>> 
p.description Arduino Due Prog_ Port 
p.interface None 
p.name None 
p.serial_number 855313034313519121D0 
p.vid 10755 
p.device /dev/cu.usbmodem14101 
p.location 20-1 
p.pid 61 
p.usb_description <bound method ListPortInfo.usb_description of <serial.tools.list_ports_common.ListPortInfo object at 0x10db16780>> 

===========
p.apply_usb_info <bound method ListPortInfo.apply_usb_info of <serial.tools.list_ports_common.ListPortInfo object at 0x10db167b8>> 
p.hwid USB VID:PID=2341:003E LOCATION=20-2 
p.manufacturer Arduino LLC 
p.product Arduino Due 
p.usb_info <bound method ListPortInfo.usb_info of <serial.tools.list_ports_common.ListPortInfo object at 0x10db167b8>> 
p.description Arduino Due 
p.interface None 
p.name None 
p.serial_number None 
p.vid 9025 
p.device /dev/cu.usbmodem14201 
p.location 20-2 
p.pid 62 
p.usb_description <bound method ListPortInfo.usb_description of <serial.tools.list_ports_common.ListPortInfo object at 0x10db167b8>> 

===========


'''
