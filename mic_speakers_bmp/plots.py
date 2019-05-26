import matplotlib.pyplot as plt
import scipy.io.wavfile
import pathlib

for wav in pathlib.Path('records').glob('*.wav'):
    png = wav.with_suffix('.png')
    if not png.exists():
        print('making', png)

        fs, y = scipy.io.wavfile.read(wav)

        plt.figure(figsize=(18, 12))
        plt.specgram(y, NFFT=2 ** 13, Fs=fs, noverlap=7900, cmap='inferno')
        plt.ylim([3e1, 4e4])
        plt.semilogy()
        plt.title(wav.stem)
        plt.savefig(png, transparent=True)
        # plt.show()
