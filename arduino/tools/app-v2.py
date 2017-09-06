from scipy.fftpack import fft
from PyQt5 import QtCore, QtGui  # (the example applies equally well to PySide)
import pyqtgraph as pg
import numpy as np
import generator


def plots_update():
    global signal_widget, signal_curve, fft_widget, fft_curve, first_draw_flag

    t, y, rate, seconds, n = generator.signal(rate=4096, seconds=1)

    # numpy.fft
    # f = np.fft.rfftfreq(n, d=1./rate)
    # a = np.fft.rfft(y)

    # scipy.fftpack
    f = np.fft.rfftfreq(n - 1, d=1./rate)
    a = fft(y)[:n//2] # chose only real part

    # pyFFTW
    # TODO ...
    
    a = np.abs(a / n) # normalisation
    
    signal_curve.setData(t, y)
    fft_curve.setData(f, a)

    if first_draw_flag:
        signal_widget.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
        fft_widget.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
        first_draw_flag = False


## Always start by initializing Qt (only once per application)
app = QtGui.QApplication([])

## Define a top-level widget to hold everything
w = QtGui.QWidget()
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
# pg.setConfigOptions(antialias=True)

# signal plot
signal_widget = pg.PlotWidget(title="Signal")
signal_widget.showGrid(x=True, y=True, alpha=0.3)
signal_widget.setYRange(0, 0.5)
signal_curve = signal_widget.plot(pen='b')


# fft plot
fft_widget = pg.PlotWidget(title="FFT")
fft_widget.showGrid(x=True, y=True, alpha=0.3)
fft_widget.setLogMode(x=True, y=True)
fft_curve = fft_widget.plot(pen='r')

# for perfect autoscaling 
first_draw_flag = True 

# updating the plots
timer = QtCore.QTimer()
timer.timeout.connect(plots_update) # updateplot on each timertick
timer.start(0) # Timer tick. Set 0 to update as fast as possible

# record_start_button = QtGui.QPushButton("Record")
# hbox.addWidget(self.record_start_button)

## Create a grid layout to manage the widgets size and position
layout = QtGui.QGridLayout()
w.setLayout(layout)

# google how to make layouts 
layout.addWidget(signal_widget, 0, 0)  # plot goes on right side, spanning 3 rows
layout.addWidget(fft_widget, 1, 0)  # plot goes on right side, spanning 3 rows

## Display the widget as a new window
w.show()

## Start the Qt event loop
app.exec_()
