import numpy as np
import matplotlib.pyplot as plt
myarray = np.fromfile('adc001.dat',dtype=int)
plt.plot(myarray)
plt.show()
print(myarray)