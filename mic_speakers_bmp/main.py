# # globals
# global gui, ser_reader_thread, chunkSize
# chunkSize = 256
# chunks    = 2000
#
# # init gui
# app = QtGui.QApplication(sys.argv)
# gui = AppGUI() # create class instance
#
# # init and run serial arduino reader
# ser_reader_thread = SerialReader(
#     mean_ready_signal=gui.mean_ready,
#     matrix_updated_signal=gui.matrix_updated,
#     chunkSize=chunkSize,
#     chunks=chunks
# )
# ser_reader_thread.start()
#
# # app exit
# signal.signal(signal.SIGINT, signal.SIG_DFL)
# sys.exit(app.exec())

# import time



import PyQt5.QtWidgets
import gui

# TODO: move this arduino stuff to separate class / file constructor
import sys
sys.path.append('/Users/tandav/Documents/spaces/arduino')

# import arduino
#
# arduino = arduino.find_device()
#
# print(arduino)

# chunkSize = 256
#
# while True:
#     data = port.read(chunkSize * 2)
#     print('-'*80)
#     print(data)





# while True:
#     z = arduino.read_all()
#     print(z, z.decode())
#     time.sleep(1)

if __name__ == '__main__':
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    gui = gui.GUI()
    gui.show()
    # gui.exec()
    # app.exec()

    # app = QApplication(sys.argv)

    # w = QWidget()
    # w.show()

    app.exec()
