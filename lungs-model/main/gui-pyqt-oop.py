from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtGui import QApplication
import pyqtgraph as pg
import numpy as np
import sys
import math


class AppGUI(QtGui.QWidget):

    def __init__(self, ):
        super(AppGUI, self).__init__()
        self.data = np.random.random(size=(16, 512, 512)).astype(np.float32)
        self.current_slice = self.data.shape[0] // 2
        self.init_ui()
        self.qt_connections()


    def init_ui(self):
        pg.setConfigOption('background', 'w')

        self.setGeometry(50, 50, 700, 700)
        self.setWindowTitle('Lungs Model')

        self.label = QtGui.QLabel(f'Current Slice: {self.current_slice}/{self.data.shape[0] - 1}')
        self.label.setGeometry(100, 200, 100, 100)


        self.layout = QtGui.QVBoxLayout()

        self.glayout = pg.GraphicsLayoutWidget()
        self.glayout.ci.layout.setContentsMargins(0, 0, 0, 0)

        self.img = pg.ImageItem(border='r')

        self.img.setImage(self.data[self.current_slice])

        self.view = self.glayout.addViewBox(lockAspect=True, enableMouse=False)
        self.view.addItem(self.img)

        self.step_button = QtGui.QPushButton('Step')
        
        self.progress_bar = QtGui.QProgressBar()
        self.progress_bar.setValue(self.current_slice / (self.data.shape[0] - 1) * 100)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.glayout)
        self.layout.addWidget(self.step_button)

        self.setLayout(self.layout)

        # self.setGeometry(0, 0, 512, 512)
        self.show()

    def qt_connections(self):
        self.step_button.clicked.connect(self.step)


    def step(self):
        print('step')
        self.data = np.random.random(size=(16, 512, 512)).astype(np.float32)
        self.img.setImage(self.data[self.current_slice])

    def wheelEvent(self,event):
        self.current_slice = np.clip(self.current_slice + np.sign(event.angleDelta().y()), 0, self.data.shape[0] - 1)
        self.label.setText(f'Current Slice: {self.current_slice}/{self.data.shape[0] - 1}')
        self.img.setImage(self.data[self.current_slice])
        self.progress_bar.setValue(self.current_slice / (self.data.shape[0] - 1) * 100)

        
app = QtGui.QApplication(sys.argv)
gui = AppGUI()
sys.exit(app.exec())
