from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtGui import QApplication
import pyqtgraph as pg
import numpy as np
import sys
import signal


class LungsModel():
    l_default = 0.1
    h_default = 1
    f_default = 440

    def __init__(self, L=l_default, H=h_default, F=f_default):
        self.r = np.load('../cube-full-460-512-512.npy')[10:30, ::16, ::16]
        # self.r = np.load('../cube-full-460-512-512.npy')[::8, ::8, ::8]
        self.ro  = 1e-5 + 1.24e-3 * self.r - 2.83e-7 * self.r * self.r + 2.79e-11 * self.r * self.r * self.r
        self.c = (self.ro + 0.112) * 1.38e-6

        self.t = 0
        self.l = L # dt, time step
        self.h = H # dx = dy = dz = 1mm
        self.K = self.l / self.h * self.c
        self.K2 = self.K**2
        self.K_2_by_3 = self.K**2 / 3


        # initial conditions
        self.P_pp = np.zeros_like(self.ro) # previous previous t - 2
        self.P_p  = np.zeros_like(self.ro) # previous          t - 1
        self.P    = np.zeros_like(self.ro) # current           t

        N = self.P.shape[1]
        self.A, self.B, self.C = 2, N//2, N//2 # sound source location
        self.oA, self.oB, self.oC = 6, N//2, N//2 # sound source location

        self.f = F

        self.signal_window = 64
        self.source_signal = np.zeros(self.signal_window)
        self.observ_signal = np.zeros(self.signal_window)
        
        print(f'init model l={self.l} h={self.h} f={self.f}')

    def update_P(self):
        '''
        mb work with flat and then reshape in return
        norm by now, mb add some more optimisations in future, also cuda
        '''

        S = self.P_p.shape[0]
        N = self.P_p.shape[1]

        self.P[2:-2, 2:-2, 2:-2] = 2 * self.P_p[2:-2, 2:-2, 2:-2] - self.P_pp[2:-2, 2:-2, 2:-2]

        Z = np.zeros_like(self.P_p)
        Z[2:-2, 2:-2, 2:-2] = 22.5 * self.P_p[2:-2, 2:-2, 2:-2]
        
        cell_indeces_flat = np.arange(S * N * N).reshape(S, N, N)[2:-2, 2:-2, 2:-2].flatten().reshape(-1, 1) # vertical vector

        s1_indexes_flat = cell_indeces_flat + np.array([-1, 1, -N, N, -N**2, N**2])      # i±1 j±1 k±1 
        s2_indexes_flat = cell_indeces_flat + np.array([-1, 1, -N, N, -N**2, N**2]) * 2  # i±2 j±2 k±2 
        s1_values = self.P_p.flatten()[s1_indexes_flat] # each row contains 6 neighbors of cell 
        s2_values = self.P_p.flatten()[s2_indexes_flat] # each row contains 6 neighbors of cell 
        s1 = np.sum(s1_values, axis=1) # sum by axis=1 is faster for default order
        s2 = np.sum(s2_values, axis=1)

        Z[2:-2, 2:-2, 2:-2] -=   4 * s1.reshape(S-4, N-4, N-4)
        Z[2:-2, 2:-2, 2:-2] += 1/4 * s2.reshape(S-4, N-4, N-4)

        m1 = np.array([1, -1, -1/8, -1/8])
        m2 = np.array([1, -1])

        s3_V_indexes = cell_indeces_flat + np.array([N**2, -N**2, 2*N**2, -2*N**2])
        s3_V_values = self.P_p.flatten()[s3_V_indexes] * m1 # po idee mozhno za skobki kak to vinesti m1 i m2
        s3_V_sum = np.sum(s3_V_values, axis=1)
        s3_N_indexes = cell_indeces_flat + np.array([N**2, -N**2])
        s3_N_values = self.ro.flatten()[s3_N_indexes] * m2
        s3_N_sum = np.sum(s3_N_values, axis=1)
        s3 = (s3_V_sum * s3_N_sum).reshape(S-4, N-4, N-4)
        
        s4_V_indexes = cell_indeces_flat + np.array([N, -N, 2*N, -2*N])
        s4_V_values = self.P_p.flatten()[s4_V_indexes] * m1
        s4_V_sum = np.sum(s4_V_values, axis=1)
        s4_N_indexes = cell_indeces_flat + np.array([N, -N])
        s4_N_values = self.ro.flatten()[s4_N_indexes] * m2
        s4_N_sum = np.sum(s4_N_values, axis=1)
        s4 = (s4_V_sum * s4_N_sum).reshape(S-4, N-4, N-4)

        s5_V_indexes = cell_indeces_flat + np.array([1, -1, 2, -2])
        s5_V_values = self.P_p.flatten()[s5_V_indexes] * m1
        s5_V_sum = np.sum(s5_V_values, axis=1)
        s5_N_indexes = cell_indeces_flat + np.array([1, -1])
        s5_N_values = self.ro.flatten()[s5_N_indexes] * m2
        s5_N_sum = np.sum(s5_N_values, axis=1)
        s5 = (s5_V_sum * s5_N_sum).reshape(S-4, N-4, N-4)

        Z[2:-2, 2:-2, 2:-2] += (s3 + s4 + s5) * self.ro[2:-2, 2:-2, 2:-2]
        self.P[2:-2, 2:-2, 2:-2] -= Z[2:-2, 2:-2, 2:-2] * self.K_2_by_3[2:-2, 2:-2, 2:-2]
        self.P[self.ro < 0.1] = 0
      
    def step(self):
        self.P_old = self.P
        self.update_P()
        self.P[self.A, self.B, self.C] = np.sin(2 * np.pi * self.f * self.t)
        self.P_pp  = self.P_p
        self.P_p   = self.P_old
        

        self.source_signal = np.roll(self.source_signal, -1)
        self.observ_signal = np.roll(self.observ_signal, -1)
        self.source_signal[-1] = self.P[self.A, self.B, self.C]
        self.observ_signal[-1] = self.P[self.oA, self.oB, self.oC]


        self.t += self.l
        



class AppGUI(QtGui.QWidget):
    steps_state = QtCore.pyqtSignal([int])

    def __init__(self):
        # super(AppGUI, self).__init__()
        super().__init__()
        
        self.model = LungsModel()

        self.data = self.model.P
        # self.z_slice = self.data.shape[0] // 2
        self.z_slice = self.model.A
        self.y_slice = self.model.B
        self.x_slice = self.model.C
        # self.signal_window = 64
        # self.source_signal = np.zeros(self.signal_window)
        # self.observ_signal = np.zeros(self.signal_window)
        # self.oA = 10
        # self.oB = 
        # self.oB


        self.init_ui()
        self.qt_connections()

    def init_ui(self):
        pg.setConfigOption('background', 'w')

        # self.setGeometry(50, 50, 700, 700)
        self.setWindowTitle('Lungs Model')
        self.l_label = QtGui.QLabel('dt')
        self.h_label = QtGui.QLabel('h')
        self.f_label = QtGui.QLabel('f')

        self.l_spin = pg.SpinBox(value=self.model.l, step=0.01, siPrefix=False, suffix='s')
        self.h_spin = pg.SpinBox(value=self.model.h, step=0.01, siPrefix=False)
        self.f_spin = pg.SpinBox(value=self.model.f, step=1, siPrefix=False)
        self.l_spin.setMaximumWidth(150)
        self.h_spin.setMaximumWidth(150)
        self.f_spin.setMaximumWidth(150)
        self.reset_params_button = QtGui.QPushButton('Defaults')
        self.reinit_button = QtGui.QPushButton('Restart Model')
        self.model_params_layout = QtGui.QHBoxLayout()
        self.model_params_layout.addWidget(self.l_label)
        self.model_params_layout.addWidget(self.l_spin)
        self.model_params_layout.addWidget(self.h_label)
        self.model_params_layout.addWidget(self.h_spin)
        self.model_params_layout.addWidget(self.f_label)
        self.model_params_layout.addWidget(self.f_spin)
        self.model_params_layout.addWidget(self.reset_params_button)
        self.model_params_layout.addWidget(self.reinit_button)

        self.z_slice_label = QtGui.QLabel(f'Current Z-Axis Slice: {self.z_slice + 1}/{self.data.shape[0]}')
        self.y_slice_label = QtGui.QLabel(f'Current Y-Axis Slice: {self.y_slice + 1}/{self.data.shape[1]}')
        self.x_slice_label = QtGui.QLabel(f'Current X-Axis Slice: {self.x_slice + 1}/{self.data.shape[2]}')
        self.z_slice_label.setGeometry(100, 200, 100, 100)
        self.y_slice_label.setGeometry(100, 200, 100, 100)
        self.x_slice_label.setGeometry(100, 200, 100, 100)


        self.arrays_to_vis = [QtGui.QRadioButton('P'), QtGui.QRadioButton('r'), QtGui.QRadioButton('ro'), QtGui.QRadioButton('c'), QtGui.QRadioButton('K')]
        self.arrays_to_vis[0].setChecked(True)
        self.radio_layout = QtGui.QHBoxLayout()

        for rad in self.arrays_to_vis:
            self.radio_layout.addWidget(rad)
            rad.clicked.connect(self.array_to_vis_changed)



        self.layout = QtGui.QVBoxLayout()

        # self.autolevels = False
        self.autolevels = True
        self.levels = (0, 100)
        # self.view.addItem(self.z_slice_img)
        self.glayout = pg.GraphicsLayoutWidget()
        self.glayout.ci.layout.setContentsMargins(0, 0, 0, 0)
        self.z_slice_img = pg.ImageItem(autoLevels=self.autolevels, levels=self.levels, border='b')
        self.z_slice_img.setImage(self.data[self.z_slice])
        self.view = self.glayout.addViewBox(lockAspect=True, enableMouse=False)
        self.view.addItem(self.z_slice_img)

        # self.z_slice_img.setRect(QtCore.QRect(0, 0, 50, 50))

        self.y_slice_img = pg.ImageItem(autoLevels=self.autolevels, levels=self.levels, border='r')
        self.y_slice_img.setImage(self.data[:, self.y_slice, :])
        self.y_slice_view = self.glayout.addViewBox(lockAspect=True, enableMouse=False)
        self.y_slice_view.addItem(self.y_slice_img)

        self.x_slice_img = pg.ImageItem(autoLevels=self.autolevels, levels=self.levels, border='g')
        self.x_slice_img.setImage(self.data[:, :, self.x_slice])
        self.x_slice_view = self.glayout.addViewBox(lockAspect=True, enableMouse=False)
        self.x_slice_view.addItem(self.x_slice_img)
        # print(self.data[:, self.model.B, :])


        #--------------------------- signal plots ------------------------
        plots_font = QtGui.QFont()
        fontsize = 9
        plots_font.setPixelSize(fontsize)
        plots_height = 250

        self.source_plot = pg.PlotWidget(title=f'Acoustic Pressure at P[{self.model.A}, {self.model.B}, {self.model.C}] (sound source)')
        self.source_plot.showGrid(x=True, y=True, alpha=0.1)
        self.source_plot.setYRange(-1, 1) # w\o np.log(a)
        # self.fft_widget.setYRange(-15, 0) # w/ np.log(a)
        self.source_plot.getAxis('bottom').setStyle(tickTextOffset = fontsize)
        self.source_plot.getAxis('left').setStyle(tickTextOffset = fontsize)
        self.source_plot.getAxis('bottom').tickFont = plots_font
        self.source_plot.getAxis('left').tickFont = plots_font
        self.source_plot.setMaximumHeight(plots_height)
        self.source_curve = self.source_plot.plot(pen='b')


        self.observ_plot = pg.PlotWidget(title=f'Acoustic Pressure at P[{self.model.oA}, {self.model.oB}, {self.model.oC}]')
        self.observ_plot.showGrid(x=True, y=True, alpha=0.1)
        self.observ_plot.getAxis('bottom').setStyle(tickTextOffset = fontsize)
        self.observ_plot.getAxis('left').setStyle(tickTextOffset = fontsize)
        self.observ_plot.getAxis('bottom').tickFont = plots_font
        self.observ_plot.getAxis('left').tickFont = plots_font
        self.observ_plot.setMaximumHeight(plots_height)
        self.observ_curve = self.observ_plot.plot(pen='r')

        self.plots_layout = QtGui.QHBoxLayout()
        # self.plots_layout.addStretch()
        # self.plots_layout.setMinimumWidth(200)
        self.plots_layout.addWidget(self.source_plot)
        self.plots_layout.addWidget(self.observ_plot)

        #----------------------------------------------------------------

        self.step_layout = QtGui.QHBoxLayout()
        self.steps_label = QtGui.QLabel('Number of steps: ')
        self.steps_spin = QtGui.QSpinBox()
        self.steps_spin.setRange(1, 10000)
        self.steps_spin.setValue(1)
        self.steps_spin.setMaximumWidth(100)
        # self.steps_spin.setMaximumSize(100, 50)
        # self.steps_spin.setGeometry(QtCore.QRect(10, 10, 50, 21))
        self.step_button = QtGui.QPushButton('Step')
        # self.step_button.setMaximumSize(100, 50)
        self.step_button.setMaximumWidth(100)
        self.steps_progress_bar = QtGui.QProgressBar()
        self.step_layout.addWidget(self.steps_label)
        self.step_layout.addWidget(self.steps_spin)
        self.step_layout.addWidget(self.step_button)
        self.step_layout.addWidget(self.steps_progress_bar)
        

        self.z_slice_slider = QtGui.QSlider()
        self.z_slice_slider.setOrientation(QtCore.Qt.Horizontal)
        self.z_slice_slider.setRange(0, self.data.shape[0] - 1)
        self.z_slice_slider.setValue(self.z_slice)
        self.z_slice_slider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.z_slice_slider.setTickInterval(1)
        
        self.y_slice_slider = QtGui.QSlider()
        self.y_slice_slider.setOrientation(QtCore.Qt.Horizontal)
        self.y_slice_slider.setRange(0, self.data.shape[1] - 1)
        self.y_slice_slider.setValue(self.y_slice)
        self.y_slice_slider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.y_slice_slider.setTickInterval(1)

        self.x_slice_slider = QtGui.QSlider()
        self.x_slice_slider.setOrientation(QtCore.Qt.Horizontal)
        self.x_slice_slider.setRange(0, self.data.shape[1] - 1)
        self.x_slice_slider.setValue(self.x_slice)
        self.x_slice_slider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.x_slice_slider.setTickInterval(1)

        self.layout.addLayout(self.model_params_layout)
        self.layout.addLayout(self.radio_layout)
        self.layout.addWidget(self.z_slice_label)
        self.layout.addWidget(self.z_slice_slider)
        self.layout.addWidget(self.y_slice_label)
        self.layout.addWidget(self.y_slice_slider)
        self.layout.addWidget(self.x_slice_label)
        self.layout.addWidget(self.x_slice_slider)
        self.layout.addWidget(self.glayout)
        self.layout.addLayout(self.plots_layout)
        # self.layout.addWidget(self.source_plot)
        # self.layout.addWidget(self.observ_plot)
        self.layout.addLayout(self.step_layout)

        self.setLayout(self.layout)

        self.setGeometry(0, 0, 1200, 900)
        self.show()

    def qt_connections(self):
        self.step_button.clicked.connect(self.do_steps)
        self.l_spin.valueChanged.connect(self.l_spin_value_changed)
        self.h_spin.valueChanged.connect(self.h_spin_value_changed)
        self.f_spin.valueChanged.connect(self.f_spin_value_changed)
        self.reset_params_button.clicked.connect(self.reset_params)
        self.reinit_button.clicked.connect(self.reinit_model)
        self.z_slice_slider.valueChanged.connect(self.z_slice_slider_changed)
        self.y_slice_slider.valueChanged.connect(self.y_slice_slider_changed)
        self.x_slice_slider.valueChanged.connect(self.x_slice_slider_changed)
        self.steps_state.connect(self.update_steps_progress_bar)

    # def mouseMoved(self, event):
        # print('mouseMoved event')

    def mouseMoveEvent(self, ev):
        print('pp')

    def l_spin_value_changed(self):
        self.model.l = self.l_spin.value()

    def h_spin_value_changed(self):
        self.model.h = self.h_spin.value()
    
    def f_spin_value_changed(self):
        self.model.f = self.f_spin.value()

    @QtCore.pyqtSlot(int)
    def update_steps_progress_bar(self, current_step):
        self.steps_progress_bar.setValue(current_step / self.steps_spin.value() * 100)
        QApplication.processEvents() 

    def reset_params(self):
        self.l_spin.setValue(LungsModel.l_default)
        self.h_spin.setValue(LungsModel.h_default)
        self.f_spin.setValue(LungsModel.f_default)

        self.z_slice = self.model.A
        self.y_slice = self.model.B
        self.x_slice = self.model.C
        self.z_slice_slider.setValue(self.z_slice)
        self.y_slice_slider.setValue(self.y_slice)
        self.x_slice_slider.setValue(self.x_slice)

        self.arrays_to_vis[0].setChecked(True)
        self.array_to_vis_changed()

    def reinit_model(self):
        self.model = LungsModel(self.l_spin.value(), self.h_spin.value(), self.f_spin.value())
        self.array_to_vis_changed()

    def array_to_vis_changed(self):
        
        mapping = {
            'P' : self.model.P,
            'r' : self.model.r,
            'ro': self.model.ro,
            'c' : self.model.c,
            'K' : self.model.K,
        }

        for r in self.arrays_to_vis:
            if r.isChecked():
                self.data = mapping[r.text()]
                self.z_slice_img.setImage(self.data[self.z_slice      ])
                self.y_slice_img.setImage(self.data[:, self.y_slice, :])
                self.x_slice_img.setImage(self.data[:, :, self.x_slice])

    def print_mean(self):
        # pass
        print(f'slices mean Z, Y, X   {np.mean(self.data[self.z_slice]):8.3e}    {np.mean(self.data[:, self.y_slice, :]):8.3e}    {np.mean(self.data[:, :, self.x_slice]):8.3e}    cube mean: {np.mean(self.data):8.3e}')

    def do_steps(self):
        for i in range(self.steps_spin.value()):
            self.model.step()
            self.z_slice_img.setImage(self.data[self.z_slice      ])
            self.y_slice_img.setImage(self.data[:, self.y_slice, :])
            self.x_slice_img.setImage(self.data[:, :, self.x_slice])
            self.source_curve.setData(self.model.source_signal)
            self.observ_curve.setData(self.model.observ_signal)
            self.steps_state.emit(i + 1)
            self.print_mean()
        self.steps_state.emit(0)       

    def wheelEvent(self, event):
        pass
        # print(self.z_slice_img.boundingRect(), self.z_slice_img.sceneBoundingRect().width(), self.z_slice_img.width(), event.x())
        # print(self.z_slice_img.sceneBoundingRect(), self.z_slice_img.height(), event.pos(), event.globalPos())
        # if self.z_slice_img.boundingRect().contains(event.pos()):
        # if self.z_slice_img.sceneBoundingRect().contains(event.pos()):
        # if self.z_slice_img.sceneBoundingRect().contains(event.globalPos()):
            # self.z_slice = np.clip(self.z_slice + np.sign(event.angleDelta().y()), 0, self.data.shape[0] - 1) # change bounds 0..N-1 => 1..N
            # self.z_slice_slider.setValue(self.z_slice)

    def keyPressEvent(self, event):
        if type(event) == QtGui.QKeyEvent and event.key() == QtCore.Qt.Key_Up:
            self.do_steps()
            #here accept the event and do something
            # self.record_values_button_clicked()
            event.accept()
        else:
            event.ignore()

    def z_slice_slider_changed(self):
        self.z_slice = self.z_slice_slider.value()
        self.z_slice_label.setText(f'Current Z-Axis Slice: {self.z_slice + 1}/{self.data.shape[0]}')
        self.z_slice_img.setImage(self.data[self.z_slice])
        self.print_mean()

    def y_slice_slider_changed(self):
        self.y_slice = self.y_slice_slider.value()
        self.y_slice_label.setText(f'Current Y-Axis Slice: {self.y_slice + 1}/{self.data.shape[1]}')
        self.y_slice_img.setImage(self.data[:, self.y_slice, :])
        self.print_mean()

    def x_slice_slider_changed(self):
        self.x_slice = self.x_slice_slider.value()
        self.x_slice_label.setText(f'Current X-Axis Slice: {self.x_slice + 1}/{self.data.shape[2]}')
        self.x_slice_img.setImage(self.data[:, :, self.x_slice])
        self.print_mean()




app = QtGui.QApplication(sys.argv)
# print(sys.argv[1])
gui = AppGUI()
signal.signal(signal.SIGINT, signal.SIG_DFL)
sys.exit(app.exec())
