from math import *
import matplotlib.pyplot as plt

x = range(300)
y = [sin(i) for i in x]
plt.plot(x, y)
# plt.axis('equal')
plt.show()
