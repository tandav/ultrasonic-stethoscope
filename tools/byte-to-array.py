import serial

ser = serial.Serial('/dev/cu.usbmodem1421', 250000)

buffer = []

while True:
    try:
        # bytesToRead = ser.inWaiting()
        # raw_bytes = ser.read(bytesToRead)
        raw_bytes = ser.read_all()
        
        if len(raw_bytes) > 1:
            # print(raw_bytes)
            bytes_array = raw_bytes.split(b'\r\n')
            for b in bytes_array:
                try:
                    buffer.append(float(b))
                except Exception as e:
                    pass
                    # print("float conversion error:", e)
            print(len(buffer))
            print("----------------")

        # print(ser.read_all)
        # y = np.append(y, float(ser.readline()))
        # y = np.delete(y, 0)
    except Exception as e:
        # pass
        # print(e)
        print("Serial readline() error:", e)
