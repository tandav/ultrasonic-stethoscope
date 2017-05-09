import serial

ser = serial.Serial('/dev/cu.usbmodem1421', 9600)

while True:
    # bytesToRead = ser.inWaiting()
    # print ser.read(bytesToRead)
    print ser.readline()
