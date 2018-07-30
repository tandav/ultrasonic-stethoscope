from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
import pyqtgraph.ptime as ptime

app = QtGui.QApplication([])
pg.setConfigOption('background', 'w')
## Create window with GraphicsView widget
win = pg.GraphicsLayoutWidget()
win.show()  ## show widget alone in its own window
win.setWindowTitle('pyqtgraph example: ImageItem')
view = win.addViewBox()

## lock the aspect ratio so pixels are always square
view.setAspectLocked(True)

## Create image item
img = pg.ImageItem(border='b')
view.addItem(img)

## Set initial view bounds
view.setRange(QtCore.QRectF(0, 0, 600, 600))

## Create random image
data = np.random.random(size=(16, 512, 512)).astype(np.float32)
img.setImage(data[0])

# i = 0

# updateTime = ptime.time()
# fps = 0

# def updateData():
#     global img, data, i, updateTime, fps

#     ## Display the data
#     img.setImage(data[i])
#     i = (i+1) % data.shape[0]

#     # QtCore.QTimer.singleShot(1, updateData)
#     now = ptime.time()
#     fps2 = 1.0 / (now-updateTime)
#     updateTime = now
#     fps = fps * 0.9 + fps2 * 0.1
    
#     # print("%0.1f fps" % fps)
#     print(f'{fps} fps')
    

# updateData()

QtGui.QApplication.instance().exec_()
