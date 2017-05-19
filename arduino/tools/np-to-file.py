import numpy as np
# open('asd.txt', 'w').close() # clear the file

# f=open('data.dat','wb')
f=open('data.dat','w')

# for i in range(1000000):
#   x = np.array([i, 7.7])
#   np.savetxt(f, x)

# x = np.arange(0,10,0.1, dtype=np.float32)
# np.savetxt(f, x)

x = np.array([], dtype=np.float32)

with open('data.dat', 'w') as f:
	for i in range(20):
		x = np.append(x, np.array([i]))
	x.tofile(f)

print(x)

import gzip
import shutil
with open('data.dat', 'rb') as f_in, gzip.open('data.dat.gz', 'wb') as f_out:
    shutil.copyfileobj(f_in, f_out)
