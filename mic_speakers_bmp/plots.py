import matplotlib.pyplot as plt
import scipy.io.wavfile
import pathlib

for wav in pathlib.Path('records').glob('*.wav'):
    png = wav.with_suffix('.png')
    if not png.exists():
        print('making', png)

        fs, y = scipy.io.wavfile.read(wav)

        # plt.figure(figsize=(18, 12))
        # plt.specgram(y, NFFT=2 ** 13, Fs=fs, noverlap=7900, cmap='inferno')
        # plt.ylim([3e1, 4e4])
        # plt.semilogy()

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 9))

        ax1.specgram(y, NFFT=2 ** 13, Fs=fs, noverlap=7900, cmap='inferno')
        ax1.set_ylim([3e1, fs//2])
        ax1.semilogy()

        ax2.plot(y, 'k-', lw=0.2)
        ax2.grid(linestyle='--', lw=0.5)

        plt.suptitle(wav.stem)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(png, dpi=80, transparent=True)
        # plt.show()

