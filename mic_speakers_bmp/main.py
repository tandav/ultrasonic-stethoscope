import PyQt5.QtWidgets
import gui
import threading
import serial_port

import signal
# import simple_reader


import sys


# while True:
#     z = arduino.read_all()
#     print(z, z.decode())
#     time.sleep(1)





if __name__ == '__main__':
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    gui = gui.GUI()




    def ctrl_c_handler(sig, frame):
        serial_port.stop_flag = True
        app.quit()



    signal.signal(signal.SIGINT, ctrl_c_handler)

    serial_reader = threading.Thread(
        target=serial_port.run,
        args=(gui.bmp_signal, gui.mic_signal)
    )

    # serial_reader = threading.Thread(
    #     target=simple_reader.run,
    #     args=(gui.data_collected_signal,)
    # )
    serial_reader.start()

    gui.show()

    app.exec()

