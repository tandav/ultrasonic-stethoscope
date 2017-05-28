# CUDA FFT Server
- decompress gzip > .dat
- .dat > signal-array (whole or by parts)
- signal-array > fft_arrray
- fft_arrray > fft.png > file
- fft.png > socket > macbook (client)

## Run Server Instructions
- [here will be links to .dll, CudaLib.cs]
- install cuda toolkit
- run in x64 mode instead of AnyCPU (set in visual studio)
- no need to add reference to dll
- put dll in bin/x64/Debug (when debug)
- just run it!
