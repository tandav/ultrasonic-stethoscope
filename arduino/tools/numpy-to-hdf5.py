import h5py
import numpy as np

with h5py.File('to_cuda.h5', 'w') as f:
	x = np.arange(10, dtype=np.float32)
	print(x)
	f.create_dataset('adc_samples', data=x, compression='lzf')
