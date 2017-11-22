import glob
import os
import sys

print(os.system('pwd'))

with open('data.dat', 'w') as f:
    for i in range(20):
        x = np.append(x, np.array([i]))
    x.tofile(f)

# f =open('data.dat','w')


# print()

print(glob.glob('./*.dat'))

