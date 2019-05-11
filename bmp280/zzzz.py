from pyqtgraph.Qt import QtGui
from PyQt5.QtGui import QApplication
import pyqtgraph as pg
import numpy as np
import sys
import signal
import struct
import PyQt5.QtCore
import serial # TODO: try del
import serial.tools.list_ports
import time

import sys; sys.path.append('/Users/tandav/Documents/spaces/arduino'); import arduino
port = arduino.find_device()



class AppGUI(QtGui.QWidget):
    steps_state = PyQt5.QtCore.pyqtSignal([int])

    def __init__(self):
        super(AppGUI, self).__init__()

        self.port = arduino.find_device()

        # self.n = 800
        self.n = 400

        self.sensor_0 = np.full(self.n, np.nan)
        self.sensor_1 = np.full(self.n, np.nan)

        self.difference = np.zeros(self.n)


        self.i = 0

        self.init_ui()
        self.timer = PyQt5.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(0)



    def init_ui(self):
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        self.layout = QtGui.QVBoxLayout()

        self.signal_plot = pg.PlotWidget()
        self.diff_plot = pg.PlotWidget()

        self.signal_plot.showGrid(x=True, y=True, alpha=0.1)
        self.diff_plot.showGrid(x=True, y=True, alpha=0.1)

        # self.plot = pg.PlotWidget()

        
        self.layout.addWidget(self.signal_plot)
        self.layout.addWidget(self.diff_plot)

        self.sensor_0_curve = self.signal_plot.plot(pen='b')
        self.sensor_1_curve = self.signal_plot.plot(pen='r')
        self.difference_curve = self.diff_plot.plot(pen='g')

        self.setLayout(self.layout)
        self.setGeometry(10, 10, 1000, 600)
        self.show()

    def update(self):
        # self.sensor_0   = np.random.random(100)
        # self.sensor_1   = np.random.random(100)
        # self.difference = np.random.random(100)
        
        # tmp = self.port.read_all() # refresh
        # print(tmp)
        # print(len(tmp))

        # print(len(tmp))

        sensor_0_bytes = self.port.read(4)
        sensor_1_bytes = self.port.read(4)

        s0, = struct.unpack('f', sensor_0_bytes)
        s1, = struct.unpack('f', sensor_1_bytes)

        s0 /= 100_000
        s1 /= 100_000

        # self.sensor_0   = np.roll(self.sensor_0, -1); self.sensor_0[-1] = s0
        # self.sensor_1   = np.roll(self.sensor_1, -1); self.sensor_1[-1] = s1
        # self.difference = np.roll(self.difference, -1); self.difference[-1] = abs(s0 - s1)
        
        dp = 0.0005

        if s0 - s1 > dp:
            state = 'inhale'
        elif s1 - s0 > dp:
            state = 'exhale'
        else:
            state = 'normal' 
        print(f'blue: {s0:.5f}, red {s1:.5f} {state}')
        if self.i == self.n:
            self.sensor_0[:] = float('nan')
            self.sensor_1[:] = float('nan')
            self.difference[:] = float('nan')
            self.i = 0

        self.sensor_0[self.i] = s0
        self.sensor_1[self.i] = s1
        # self.difference[self.i] = abs(s0 - s1)
        self.difference[self.i] = s0 - s1

        self.sensor_0_curve.setData(self.sensor_0)
        self.sensor_1_curve.setData(self.sensor_1)
        self.difference_curve.setData(self.difference)

        self.i += 1

app = QtGui.QApplication(sys.argv)
# print(sys.argv[1])
gui = AppGUI()
signal.signal(signal.SIGINT, signal.SIG_DFL)
sys.exit(app.exec())
