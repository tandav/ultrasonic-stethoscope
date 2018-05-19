from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtGui import QApplication
import pyqtgraph as pg
import numpy as np
import sys
import signal
from time import time, sleep

class AppGUI(QtGui.QWidget):
    steps_state = QtCore.pyqtSignal([int])

    def __init__(self, P):
        super(AppGUI, self).__init__()
        

        self.data = P
        # self.current_slice = self.data.shape[0] // 2
        self.current_slice = A
        
        self.init_ui()
        self.qt_connections()


    def init_ui(self):
        pg.setConfigOption('background', 'w')

        self.setGeometry(50, 50, 700, 700)
        self.setWindowTitle('Lungs Model')

        self.label = QtGui.QLabel(f'Current Slice: {self.current_slice}/{self.data.shape[0] - 1}')
        self.label.setGeometry(100, 200, 100, 100)


        self.arrays_to_vis = [QtGui.QRadioButton('P'), QtGui.QRadioButton('r'), QtGui.QRadioButton('ro'), QtGui.QRadioButton('c'), QtGui.QRadioButton('K')]
        self.arrays_to_vis[0].setChecked(True)
        self.radio_layout = QtGui.QHBoxLayout()

        for rad in self.arrays_to_vis:
            self.radio_layout.addWidget(rad)
            rad.toggled.connect(self.array_to_vis_changed)

        self.mapping = {
            'P':P,
            'r':r,
            'ro':ro,
            'c':c,
            'K':K,
        }


        self.layout = QtGui.QVBoxLayout()

        self.glayout = pg.GraphicsLayoutWidget()
        self.glayout.ci.layout.setContentsMargins(0, 0, 0, 0)

        self.img = pg.ImageItem(border='b')

        self.img.setImage(self.data[self.current_slice])

        self.view = self.glayout.addViewBox(lockAspect=True, enableMouse=False)
        self.view.addItem(self.img)

        self.step_layout = QtGui.QHBoxLayout()
        self.steps_label = QtGui.QLabel('Number of steps: ')
        self.steps_spin = QtGui.QSpinBox()
        self.steps_spin.setRange(1, 100)
        self.steps_spin.setValue(1)
        self.steps_spin.setMaximumSize(100, 50)
        # self.steps_spin.setGeometry(QtCore.QRect(10, 10, 50, 21))
        self.step_button = QtGui.QPushButton('Step')
        # self.step_button.setMaximumSize(100, 50)
        self.step_button.setMaximumWidth(100)
        self.steps_progress_bar = QtGui.QProgressBar()
        self.step_layout.addWidget(self.steps_label)
        self.step_layout.addWidget(self.steps_spin)
        self.step_layout.addWidget(self.step_button)
        self.step_layout.addWidget(self.steps_progress_bar)
        
        self.progress_bar = QtGui.QProgressBar()
        self.progress_bar.setValue(self.current_slice / (self.data.shape[0] - 1) * 100)

        self.slice_slider = QtGui.QSlider()
        self.slice_slider.setOrientation(QtCore.Qt.Horizontal)
        self.slice_slider.setRange(0, self.data.shape[0] - 1)
        self.slice_slider.setValue(self.current_slice)
        self.slice_slider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.slice_slider.setTickInterval(1)


        self.layout.addLayout(self.radio_layout)
        self.layout.addWidget(self.label)
        # self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.slice_slider)
        self.layout.addWidget(self.glayout)
        self.layout.addLayout(self.step_layout)

        self.setLayout(self.layout)

        # self.setGeometry(0, 0, 512, 512)
        self.show()

    def qt_connections(self):
        self.step_button.clicked.connect(self.do_steps)
        self.slice_slider.valueChanged.connect(self.slice_slider_changed)
        self.steps_state.connect(self.update_steps_progress_bar)

    @QtCore.pyqtSlot(int)
    def update_steps_progress_bar(self, current_step):
        self.steps_progress_bar.setValue(current_step / self.steps_spin.value() * 100)
        QApplication.processEvents() 


    def array_to_vis_changed(self):
        for r in self.arrays_to_vis:
            if r.isChecked():
                self.data = self.mapping[r.text()]
                self.img.setImage(self.data[self.current_slice])

                # print(r.text())

    def do_steps(self):
        for i in range(self.steps_spin.value()):
            step()
            self.img.setImage(self.data[self.current_slice])
            self.steps_state.emit(i + 1)
        self.steps_state.emit(0)        


    def wheelEvent(self,event):
        self.current_slice = np.clip(self.current_slice + np.sign(event.angleDelta().y()), 0, self.data.shape[0] - 1)
        self.label.setText(f'Current Slice: {self.current_slice}/{self.data.shape[0] - 1}')
        self.img.setImage(self.data[self.current_slice])
        # self.progress_bar.setValue(self.current_slice / (self.data.shape[0] - 1) * 100)
        self.slice_slider.setValue(self.current_slice)

    def keyPressEvent(self, event):
        if type(event) == QtGui.QKeyEvent and event.key() == QtCore.Qt.Key_Up:
            self.do_steps()
            #here accept the event and do something
            # self.record_values_button_clicked()
            event.accept()
        else:
            event.ignore()

    def slice_slider_changed(self):
        self.current_slice = self.slice_slider.value()
        self.label.setText(f'Current Slice: {self.current_slice}/{self.data.shape[0] - 1}')
        self.img.setImage(self.data[self.current_slice])
        self.progress_bar.setValue(self.current_slice / (self.data.shape[0] - 1) * 100)


# model code start ------------------------------------------------------------

r = np.load('../3d_numpy_array_reduced-58-64-64.npy')
ro  = 1e-5 + 1.24e-3*r - 2.83e-7*r*r + 2.79e-11*r*r*r
c = (ro + 0.112) * 1.38e-6


t = 0
l = 0.1 # dt, time step
h = 1 # dx = dy = dz = 1mm
K = l / h * c
K2 = K**2
K_2_by_3 = K**2 / 3

# initial conditions
P_pp = np.zeros_like(ro) # previous previous t - 2
P_p  = np.zeros_like(ro) # previous          t - 1
P    = np.zeros_like(ro) # current           t

def p_step():
    global P
    '''
    mb work with flat and then reshape in return
    norm by now, mb add some more optimisations in future, also cuda
    '''

    S = P_p.shape[0]
    N = P_p.shape[1]

    P[2:-2, 2:-2, 2:-2] = 2 * P_p[2:-2, 2:-2, 2:-2] - P_pp[2:-2, 2:-2, 2:-2]

    Z = np.zeros_like(P_p)
    Z[2:-2, 2:-2, 2:-2] = 22.5 * P_p[2:-2, 2:-2, 2:-2]
    
    cell_indeces_flat = np.arange(S * N * N).reshape(S, N, N)[2:-2, 2:-2, 2:-2].flatten().reshape(-1, 1) # vertical vector

    s1_indexes_flat = cell_indeces_flat + np.array([-1, 1, -N, N, -N**2, N**2])      # i±1 j±1 k±1 
    s2_indexes_flat = cell_indeces_flat + np.array([-1, 1, -N, N, -N**2, N**2]) * 2  # i±2 j±2 k±2 
    s1_values = P_p.flatten()[s1_indexes_flat] # each row contains 6 neighbors of cell 
    s2_values = P_p.flatten()[s2_indexes_flat] # each row contains 6 neighbors of cell 
    s1 = np.sum(s1_values, axis=1) # sum by axis=1 is faster for default order
    s2 = np.sum(s2_values, axis=1)

    Z[2:-2, 2:-2, 2:-2] -=   4 * s1.reshape(S-4, N-4, N-4)
    Z[2:-2, 2:-2, 2:-2] += 1/4 * s2.reshape(S-4, N-4, N-4)

    m1 = np.array([1, -1, -1/8, -1/8])
    m2 = np.array([1, -1])

    s3_V_indexes = cell_indeces_flat + np.array([N**2, -N**2, 2*N**2, -2*N**2])
    s3_V_values = P_p.flatten()[s3_V_indexes] * m1 # po idee mozhno za skobki kak to vinesti m1 i m2
    s3_V_sum = np.sum(s3_V_values, axis=1)
    s3_N_indexes = cell_indeces_flat + np.array([N**2, -N**2])
    s3_N_values = ro.flatten()[s3_N_indexes] * m2
    s3_N_sum = np.sum(s3_N_values, axis=1)
    s3 = (s3_V_sum * s3_N_sum).reshape(S-4, N-4, N-4)
    
    s4_V_indexes = cell_indeces_flat + np.array([N, -N, 2*N, -2*N])
    s4_V_values = P_p.flatten()[s4_V_indexes] * m1
    s4_V_sum = np.sum(s4_V_values, axis=1)
    s4_N_indexes = cell_indeces_flat + np.array([N, -N])
    s4_N_values = ro.flatten()[s4_N_indexes] * m2
    s4_N_sum = np.sum(s4_N_values, axis=1)
    s4 = (s4_V_sum * s4_N_sum).reshape(S-4, N-4, N-4)

    s5_V_indexes = cell_indeces_flat + np.array([1, -1, 2, -2])
    s5_V_values = P_p.flatten()[s5_V_indexes] * m1
    s5_V_sum = np.sum(s5_V_values, axis=1)
    s5_N_indexes = cell_indeces_flat + np.array([1, -1])
    s5_N_values = ro.flatten()[s5_N_indexes] * m2
    s5_N_sum = np.sum(s5_N_values, axis=1)
    s5 = (s5_V_sum * s5_N_sum).reshape(S-4, N-4, N-4)

    Z[2:-2, 2:-2, 2:-2] += (s3 + s4 + s5) * ro[2:-2, 2:-2, 2:-2]
    P[2:-2, 2:-2, 2:-2] -= Z[2:-2, 2:-2, 2:-2] * K_2_by_3[2:-2, 2:-2, 2:-2]
    P[ro < 0.1] = 0
  
def step():
    global t, P, P_p, P_pp
    P_old = P
    p_step()
    P[A, B, C] = np.sin(2 * np.pi * f * t)
    P_pp  = P_p
    P_p   = P_old
    t += l

N = P.shape[1]
A, B, C = 2, N//2, N//2 # sound source location
t = 0
f = 400

# model code end -------------------------------------------------------------

        
app = QtGui.QApplication(sys.argv)
gui = AppGUI(P)
signal.signal(signal.SIGINT, signal.SIG_DFL)
sys.exit(app.exec())
