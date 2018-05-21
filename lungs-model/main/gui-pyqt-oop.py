from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtGui import QApplication
import pyqtgraph as pg
import numpy as np
import sys
import signal


class LungsModel():
    l_default = 0.065
    h_default = 0.55e-6
    f_default = 110
    # l_default = 0.1
    # h_default = 1
    # f_default = 440

    def __init__(self, L=l_default, H=h_default, F=f_default):
        # self.r = np.load('../cube-full-460-512-512.npy')
        # self.r = np.load('../cube-full-460-512-512.npy')[::1, ::1, ::1]
        # self.r = np.load('../cube-full-460-512-512.npy')[::2, ::2, ::2]
        # self.r = np.load('../cube-full-460-512-512.npy')[::4, ::4, ::4]
        # k = 11
        # self.r = np.load('../cube-full-460-512-512.npy')[::k, ::k, ::k]
        y_start = 155
        x_start = 135
        sqr = 245
        k = 3
        self.r = np.load('../cube-full-460-512-512.npy')[
            50:100:k,
            y_start : y_start + sqr : k,
            x_start : x_start + sqr : k,
        ]
        # self.r = np.load('../cube-full-460-512-512.npy')[::64, ::32, ::16]
        # self.r = np.random.random((2,3,4))
        self.r[0,0,0] = 3
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
        # self.A, self.B, self.C = 2, N//2, N//2 # sound source location
        # self.oA, self.oB, self.oC = 6, N//2, N//2 # sound source location
        self.oA, self.oB, self.oC = 4, N//2, N//2 # sound source location

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
        
        cell_indeces_flat = np.arange(S * N * N).reshape(S, N, N)[2:-2, 2:-2, 2:-2].ravel().reshape(-1, 1) # vertical vector

        s1_indexes_flat = cell_indeces_flat + np.array([-1, 1, -N, N, -N**2, N**2])      # i±1 j±1 k±1 
        s2_indexes_flat = cell_indeces_flat + np.array([-1, 1, -N, N, -N**2, N**2]) * 2  # i±2 j±2 k±2 
        s1_values = self.P_p.ravel()[s1_indexes_flat] # each row contains 6 neighbors of cell 
        s2_values = self.P_p.ravel()[s2_indexes_flat] # each row contains 6 neighbors of cell 
        s1 = np.sum(s1_values, axis=1) # sum by axis=1 is faster for default order
        s2 = np.sum(s2_values, axis=1)

        Z[2:-2, 2:-2, 2:-2] -=   4 * s1.reshape(S-4, N-4, N-4)
        Z[2:-2, 2:-2, 2:-2] += 1/4 * s2.reshape(S-4, N-4, N-4)

        m1 = np.array([1, -1, -1/8, -1/8])
        m2 = np.array([1, -1])

        s3_V_indexes = cell_indeces_flat + np.array([N**2, -N**2, 2*N**2, -2*N**2])
        s3_V_values = self.P_p.ravel()[s3_V_indexes] * m1 # po idee mozhno za skobki kak to vinesti m1 i m2
        s3_V_sum = np.sum(s3_V_values, axis=1)
        s3_N_indexes = cell_indeces_flat + np.array([N**2, -N**2])
        s3_N_values = self.ro.ravel()[s3_N_indexes] * m2
        s3_N_sum = np.sum(s3_N_values, axis=1)
        s3 = (s3_V_sum * s3_N_sum).reshape(S-4, N-4, N-4)
        
        s4_V_indexes = cell_indeces_flat + np.array([N, -N, 2*N, -2*N])
        s4_V_values = self.P_p.ravel()[s4_V_indexes] * m1
        s4_V_sum = np.sum(s4_V_values, axis=1)
        s4_N_indexes = cell_indeces_flat + np.array([N, -N])
        s4_N_values = self.ro.ravel()[s4_N_indexes] * m2
        s4_N_sum = np.sum(s4_N_values, axis=1)
        s4 = (s4_V_sum * s4_N_sum).reshape(S-4, N-4, N-4)

        s5_V_indexes = cell_indeces_flat + np.array([1, -1, 2, -2])
        s5_V_values = self.P_p.ravel()[s5_V_indexes] * m1
        s5_V_sum = np.sum(s5_V_values, axis=1)
        s5_N_indexes = cell_indeces_flat + np.array([1, -1])
        s5_N_values = self.ro.ravel()[s5_N_indexes] * m2
        s5_N_sum = np.sum(s5_N_values, axis=1)
        s5 = (s5_V_sum * s5_N_sum).reshape(S-4, N-4, N-4)

        Z[2:-2, 2:-2, 2:-2] += (s3 + s4 + s5) * self.ro[2:-2, 2:-2, 2:-2]
        self.P[2:-2, 2:-2, 2:-2] -= Z[2:-2, 2:-2, 2:-2] * self.K_2_by_3[2:-2, 2:-2, 2:-2]
        # self.P[self.ro < 0.1] = 0
      
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
        super().__init__()
        
        self.model = LungsModel()

        self.data = self.model.P
        self.observ_slice = np.zeros(self.model.signal_window)
        self.z_slice = self.model.A
        self.y_slice = self.model.B
        self.x_slice = self.model.C

        self.init_ui()
        self.qt_connections()

    def init_ui(self):
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('imageAxisOrder', 'row-major')

        self.z_axis_name = ('Head', 'Feet')
        self.y_axis_name = ('Face', 'Back')
        self.x_axis_name = ('Left Hand', 'Right Hand')


        self.layout = QtGui.QVBoxLayout()

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

        # radio buttons ------------------------------------------------------------
        self.arrays_to_vis = [QtGui.QRadioButton('P'), QtGui.QRadioButton('r'), QtGui.QRadioButton('ro'), QtGui.QRadioButton('c'), QtGui.QRadioButton('K')]
        self.arrays_to_vis[0].setChecked(True)
        # self.radio_layout = QtGui.QHBoxLayout()

        for rad in self.arrays_to_vis:
            self.model_params_layout.addWidget(rad)
            rad.clicked.connect(self.array_to_vis_changed)

        self.model_params_layout.addWidget(self.reset_params_button)
        self.model_params_layout.addWidget(self.reinit_button)

        self.z_slice_label = QtGui.QLabel(f'Z axis [{self.z_axis_name[0]} - {self.z_axis_name[1]}] Slice: {self.z_slice + 1}/{self.data.shape[0]}')
        self.y_slice_label = QtGui.QLabel(f'Y axis [{self.y_axis_name[0]} - {self.y_axis_name[1]}] Slice: {self.y_slice + 1}/{self.data.shape[1]}')
        self.x_slice_label = QtGui.QLabel(f'X axis [{self.x_axis_name[0]} - {self.x_axis_name[1]}] Slice: {self.x_slice + 1}/{self.data.shape[2]}')


        # slices plots ----------------------------------------------------------------
        
        self.autolevels = True
        self.levels = (0, 100)
        self.glayout = pg.GraphicsLayoutWidget()
        self.glayout.ci.layout.setContentsMargins(0, 0, 0, 0)
        self.glayout.ci.layout.setSpacing(0)
        self.z_slice_img = pg.ImageItem(self.data[self.z_slice, :, :], autoLevels=self.autolevels, levels=self.levels, border=pg.mkPen(color='r', width=3))
        self.y_slice_img = pg.ImageItem(self.data[:, self.y_slice, :], autoLevels=self.autolevels, levels=self.levels, border=pg.mkPen(color='g', width=3))
        self.x_slice_img = pg.ImageItem(self.data[:, :, self.x_slice], autoLevels=self.autolevels, levels=self.levels, border=pg.mkPen(color='b', width=3))
        self.z_slice_plot = self.glayout.addPlot()
        self.y_slice_plot = self.glayout.addPlot()
        self.x_slice_plot = self.glayout.addPlot()
        # self.z_slice_plot.setTitle(f'Z axis [{self.z_axis_name[0]} - {self.z_axis_name[1]}]')
        # self.y_slice_plot.setTitle(f'Y axis [{self.y_axis_name[0]} - {self.y_axis_name[1]}]')
        # self.x_slice_plot.setTitle(f'X axis [{self.x_axis_name[0]} - {self.x_axis_name[1]}]')
        self.z_slice_plot.setAspectLocked() 
        self.y_slice_plot.setAspectLocked() 
        self.x_slice_plot.setAspectLocked() 
        self.z_slice_plot.setMouseEnabled(x=False, y=False)
        self.y_slice_plot.setMouseEnabled(x=False, y=False)
        self.x_slice_plot.setMouseEnabled(x=False, y=False)
        self.z_slice_plot_y_helper1 = self.z_slice_plot.plot([0               , self.data.shape[2] ], [self.y_slice    , self.y_slice      ], pen='g')
        self.z_slice_plot_y_helper2 = self.z_slice_plot.plot([0               , self.data.shape[2] ], [self.y_slice + 1, self.y_slice + 1  ], pen='g')
        self.z_slice_plot_x_helper1 = self.z_slice_plot.plot([self.x_slice    , self.x_slice       ], [0               , self.data.shape[1]], pen='b')
        self.z_slice_plot_x_helper2 = self.z_slice_plot.plot([self.x_slice + 1, self.x_slice + 1   ], [0               , self.data.shape[1]], pen='b')
        self.y_slice_plot_z_helper1 = self.y_slice_plot.plot([0               , self.data.shape[2] ], [self.z_slice    , self.z_slice      ], pen='r')
        self.y_slice_plot_z_helper2 = self.y_slice_plot.plot([0               , self.data.shape[2] ], [self.z_slice + 1, self.z_slice + 1  ], pen='r')
        self.y_slice_plot_x_helper1 = self.y_slice_plot.plot([self.x_slice    , self.x_slice       ], [0               , self.data.shape[0]], pen='b')
        self.y_slice_plot_x_helper2 = self.y_slice_plot.plot([self.x_slice + 1, self.x_slice + 1   ], [0               , self.data.shape[0]], pen='b')
        self.x_slice_plot_z_helper1 = self.x_slice_plot.plot([0               , self.data.shape[1] ], [self.z_slice    , self.z_slice      ], pen='r')
        self.x_slice_plot_z_helper2 = self.x_slice_plot.plot([0               , self.data.shape[1] ], [self.z_slice + 1, self.z_slice + 1  ], pen='r')
        self.x_slice_plot_y_helper1 = self.x_slice_plot.plot([self.y_slice    , self.y_slice       ], [0               , self.data.shape[0]], pen='g')
        self.x_slice_plot_y_helper2 = self.x_slice_plot.plot([self.y_slice + 1, self.y_slice + 1   ], [0               , self.data.shape[0]], pen='g')
        
        self.z_slice_plot.invertY(True)
        self.y_slice_plot.invertY(True)
        self.x_slice_plot.invertY(True)
        self.z_slice_plot.setLabel('bottom', f'X axis [{self.x_axis_name[0]} - {self.x_axis_name[1]}]')
        self.z_slice_plot.setLabel('left'  , f'Y axis [{self.y_axis_name[1]} - {self.y_axis_name[0]}]')
        self.y_slice_plot.setLabel('bottom', f'X axis [{self.x_axis_name[0]} - {self.x_axis_name[1]}]')
        self.y_slice_plot.setLabel('left'  , f'Z axis [{self.z_axis_name[1]} - {self.z_axis_name[0]}]')
        self.x_slice_plot.setLabel('bottom', f'Y axis [{self.y_axis_name[0]} - {self.y_axis_name[1]}]')
        self.x_slice_plot.setLabel('left'  , f'Z axis [{self.z_axis_name[1]} - {self.z_axis_name[0]}]')
        self.z_slice_plot.addItem(self.z_slice_img)
        self.y_slice_plot.addItem(self.y_slice_img)
        self.x_slice_plot.addItem(self.x_slice_img)
        self.z_slice_img.setRect(pg.QtCore.QRectF(0, 0, self.data.shape[2], self.data.shape[1]))
        self.y_slice_img.setRect(pg.QtCore.QRectF(0, 0, self.data.shape[2], self.data.shape[0]))
        self.x_slice_img.setRect(pg.QtCore.QRectF(0, 0, self.data.shape[1], self.data.shape[0]))
        self.z_slice_img.setZValue(-1)
        self.y_slice_img.setZValue(-1)
        self.x_slice_img.setZValue(-1)

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


        self.observ_slice_plot = pg.PlotWidget(title=f'Acoustic Pressure at P[{self.z_slice}, {self.y_slice}, {self.x_slice}]')
        self.observ_slice_plot.showGrid(x=True, y=True, alpha=0.1)
        self.observ_slice_plot.getAxis('bottom').setStyle(tickTextOffset = fontsize)
        self.observ_slice_plot.getAxis('left').setStyle(tickTextOffset = fontsize)
        self.observ_slice_plot.getAxis('bottom').tickFont = plots_font
        self.observ_slice_plot.getAxis('left').tickFont = plots_font
        self.observ_slice_plot.setMaximumHeight(plots_height)
        self.observ_slice_curve = self.observ_slice_plot.plot(pen=0.8)



        self.plots_layout = QtGui.QHBoxLayout()
        # self.plots_layout.addStretch()
        # self.plots_layout.setMinimumWidth(200)
        self.plots_layout.addWidget(self.source_plot)
        self.plots_layout.addWidget(self.observ_plot)
        self.plots_layout.addWidget(self.observ_slice_plot)

        #----------------------------------------------------------------

        self.step_layout = QtGui.QHBoxLayout()
        self.steps_label = QtGui.QLabel('Number of steps: ')
        self.steps_spin = QtGui.QSpinBox()
        self.steps_spin.setRange(1, 10000)
        self.steps_spin.setValue(50)
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
        self.z_slice_slider.setStyleSheet('background-color: rgba(255, 0, 0, 0.2)')
        self.z_slice_slider.setOrientation(QtCore.Qt.Horizontal)
        self.z_slice_slider.setRange(0, self.data.shape[0] - 1)
        self.z_slice_slider.setValue(self.z_slice)
        self.z_slice_slider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.z_slice_slider.setTickInterval(1)
        
        self.y_slice_slider = QtGui.QSlider()
        self.y_slice_slider.setStyleSheet('background-color: rgba(0, 255, 0, 0.2)')
        self.y_slice_slider.setOrientation(QtCore.Qt.Horizontal)
        self.y_slice_slider.setRange(0, self.data.shape[1] - 1)
        self.y_slice_slider.setValue(self.y_slice)
        self.y_slice_slider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.y_slice_slider.setTickInterval(1)

        self.x_slice_slider = QtGui.QSlider()
        self.x_slice_slider.setStyleSheet('background-color: rgba(0, 0, 255, 0.2)')
        self.x_slice_slider.setOrientation(QtCore.Qt.Horizontal)
        self.x_slice_slider.setRange(0, self.data.shape[2] - 1)
        self.x_slice_slider.setValue(self.x_slice)
        self.x_slice_slider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.x_slice_slider.setTickInterval(1)

        self.layout.addLayout(self.model_params_layout)
        # self.layout.addLayout(self.radio_layout)
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

        self.setGeometry(0, 0, 1440, 900)
        # self.setGeometry(0, 0, 1200, 900)
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

            self.observ_slice = np.roll(self.observ_slice, -1)
            self.observ_slice[-1] = self.model.P[self.z_slice, self.y_slice, self.x_slice]
            self.observ_slice_curve.setData(self.observ_slice)

            self.steps_state.emit(i + 1)
            self.print_mean()
        self.steps_state.emit(0)       

    # def wheelEvent(self, event):
        # pass
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

    def update_observ_slice_plot(self):
        self.observ_slice_plot.getPlotItem().setTitle(f'Acoustic Pressure at P[{self.z_slice}, {self.y_slice}, {self.x_slice}]')
        self.observ_slice = np.zeros(self.model.signal_window)
        self.observ_slice_curve.setData(self.observ_slice)

    def update_slice_helpers_lines(self):
        # self.z_slice_plot_y_helper.setData([0           , self.data.shape[2] ], [self.y_slice, self.y_slice      ])
        # self.z_slice_plot_x_helper.setData([self.x_slice, self.x_slice       ], [0           , self.data.shape[1]])
        # self.y_slice_plot_z_helper.setData([0           , self.data.shape[2] ], [self.z_slice, self.z_slice      ])
        # self.y_slice_plot_x_helper.setData([self.x_slice, self.x_slice       ], [0           , self.data.shape[0]])
        # self.x_slice_plot_z_helper.setData([0           , self.data.shape[1] ], [self.z_slice, self.z_slice      ])
        # self.x_slice_plot_y_helper.setData([self.y_slice, self.y_slice       ], [0           , self.data.shape[0]])
        self.z_slice_plot_y_helper1.setData([0               , self.data.shape[2] ], [self.y_slice    , self.y_slice      ])
        self.z_slice_plot_y_helper2.setData([0               , self.data.shape[2] ], [self.y_slice + 1, self.y_slice + 1  ])
        self.z_slice_plot_x_helper1.setData([self.x_slice    , self.x_slice       ], [0               , self.data.shape[1]])
        self.z_slice_plot_x_helper2.setData([self.x_slice + 1, self.x_slice + 1   ], [0               , self.data.shape[1]])
        self.y_slice_plot_z_helper1.setData([0               , self.data.shape[2] ], [self.z_slice    , self.z_slice      ])
        self.y_slice_plot_z_helper2.setData([0               , self.data.shape[2] ], [self.z_slice + 1, self.z_slice + 1  ])
        self.y_slice_plot_x_helper1.setData([self.x_slice    , self.x_slice       ], [0               , self.data.shape[0]])
        self.y_slice_plot_x_helper2.setData([self.x_slice + 1, self.x_slice + 1   ], [0               , self.data.shape[0]])
        self.x_slice_plot_z_helper1.setData([0               , self.data.shape[1] ], [self.z_slice    , self.z_slice      ])
        self.x_slice_plot_z_helper2.setData([0               , self.data.shape[1] ], [self.z_slice + 1, self.z_slice + 1  ])
        self.x_slice_plot_y_helper1.setData([self.y_slice    , self.y_slice       ], [0               , self.data.shape[0]])
        self.x_slice_plot_y_helper2.setData([self.y_slice + 1, self.y_slice + 1   ], [0               , self.data.shape[0]])


    def z_slice_slider_changed(self):
        self.z_slice = self.z_slice_slider.value()
        self.z_slice_label.setText(f'Z axis [{self.z_axis_name[0]} - {self.z_axis_name[1]}]')
        self.z_slice_img.setImage(self.data[self.z_slice])
        self.print_mean()
        self.update_observ_slice_plot()
        self.update_slice_helpers_lines()

    def y_slice_slider_changed(self):
        self.y_slice = self.y_slice_slider.value()
        self.y_slice_label.setText(f'Y axis [{self.y_axis_name[0]} - {self.y_axis_name[1]}] Slice: {self.y_slice + 1}/{self.data.shape[1]}')
        self.y_slice_img.setImage(self.data[:, self.y_slice, :])
        self.print_mean()
        self.update_observ_slice_plot()
        self.update_slice_helpers_lines()

    def x_slice_slider_changed(self):
        self.x_slice = self.x_slice_slider.value()
        self.x_slice_label.setText(f'X axis [{self.x_axis_name[0]} - {self.x_axis_name[1]}] Slice: {self.x_slice + 1}/{self.data.shape[2]}')
        self.x_slice_img.setImage(self.data[:, :, self.x_slice])
        self.print_mean()
        self.update_observ_slice_plot()
        self.update_slice_helpers_lines()






app = QtGui.QApplication(sys.argv)
# print(sys.argv[1])
gui = AppGUI()
signal.signal(signal.SIGINT, signal.SIG_DFL)
sys.exit(app.exec())
