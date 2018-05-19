from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtGui import QApplication
import pyqtgraph as pg
import numpy as np
import time
import threading
import sys


class AppGUI(QtGui.QWidget):
    data_collected = QtCore.pyqtSignal()
    chunk_recorded = QtCore.pyqtSignal()

    def __init__(self, ):
        super(AppGUI, self).__init__()
        
        # pg.setConfigOption('background', 'w')

        self.setGeometry(50, 50, 700, 700)
        self.setWindowTitle('Lungs Model')


        self.layout = QtGui.QVBoxLayout()

        self.glayout = pg.GraphicsLayoutWidget()
        self.glayout.ci.layout.setContentsMargins(-100, 0, 0, 0)
        # self.glayout.ci.layout.setContentsMargins(0, 0, 0, 0)
        self.glayout.ci.layout.setSpacing(0)  # might not be necessary for you

        self.img = pg.ImageItem(border='r')
        data = np.random.random(size=(16, 512, 512)).astype(np.float32)
        self.img.setImage(data[0])

        self.view = self.glayout.addViewBox()
        self.view.addItem(self.img)
        
        self.layout.addWidget(self.glayout)
        self.setLayout(self.layout)
        # self.setGeometry(0, 0, 512, 512)
        self.show()

app = QtGui.QApplication(sys.argv)
gui = AppGUI()
sys.exit(app.exec())


