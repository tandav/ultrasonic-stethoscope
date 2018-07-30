import numpy as np

series_start_t         = 336_011_201
series_duration        =   1_000_000
tone_duration          =      20_000
short_silence_duration =      80_000
long_silence_duration  =   2_000_000


# cycle = tone_duration + short_silence_duration

series_duration / (tone_duration + short_silence_duration)

tone_starts = np.arange(
    series_start_t, 
    series_start_t + series_duration,
    tone_duration + short_silence_duration
)


print(tone_starts)
print(tone_starts[-1] < series_start_t + series_duration)

