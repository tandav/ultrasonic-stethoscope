import PyQt5.QtWidgets
import gui

import sys


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
