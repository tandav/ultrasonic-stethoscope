I use Vakhtin's library (dll) to work with CUDA. There is a method that calculates FFT:

```cs
CUDA.CUFT.Furie(block, fft, block_size)
``` 

Короче она выбрасывает ошибку при некоторых (9 штук) размерах массива. Как на картинке. И поэтому я юзаю массивы кратные 1000 (actually, powers of 10), а не степени двойки.

![img_1023](https://cloud.githubusercontent.com/assets/5549677/26735337/39247a32-47ca-11e7-9e86-4de3c883aa14.jpg)

Вот прога, с помощью которой я нашел эти проблемные размеры:
![img_1024](https://cloud.githubusercontent.com/assets/5549677/26735341/3b162782-47ca-11e7-9db1-39fa0be233bd.jpg)
