from PyQt5 import QtCore, QtGui  # (the example applies equally well to PySide)
import pyqtgraph as pg
import numpy as np
import generator

def plots_update():
    global fft_curve, ptr, fft_widget
    # data = np.random.rand(size=(10,1000))

    t = np.arange(100)
    y = np.random.rand(100)

    fft_curve.setData(t, y)
    if ptr == 0:
        fft_widget.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
    ptr += 1


## Always start by initializing Qt (only once per application)
app = QtGui.QApplication([])

## Define a top-level widget to hold everything
w = QtGui.QWidget()
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
# pg.setConfigOptions(antialias=True)


signal_widget = pg.PlotWidget(title="Sifnal")
signal_curve = signal_widget.plot(pen='b')



# p2 = pg.PlotWidget()
# x = np.cos(np.linspace(1, 2*np.pi, 1000))
# y = np.abs(np.sin(np.linspace(1, 4*np.pi, 1000)))
# p2.plot(x, y)
# p2.showGrid(x=True, y=True)
# p2.setLogMode(x=True, y=False)



# p6 = win.addPlot(title="Updating plot")
fft_widget = pg.PlotWidget(title="FFT")
fft_widget.setLogMode(x=True, y=False)
fft_curve = fft_widget.plot(pen='r')

ptr = 0
timer = QtCore.QTimer()
timer.timeout.connect(plots_update)
timer.start(0)



## Create a grid layout to manage the widgets size and position
layout = QtGui.QGridLayout()
w.setLayout(layout)

## Add widgets to the layout in their proper positions
# layout.addWidget(p1, 0, 1, 2, 1)  # plot goes on right side, spanning 3 rows
# layout.addWidget(p2, 5, 1, 2, 1)  # plot goes on right side, spanning 3 rows
layout.addWidget(signal_widget, 0, 0)  # plot goes on right side, spanning 3 rows
layout.addWidget(fft_widget, 1, 0)  # plot goes on right side, spanning 3 rows

## Display the widget as a new window
w.show()

## Start the Qt event loop
app.exec_()
