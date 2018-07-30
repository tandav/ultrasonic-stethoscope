# Lungs Model
- This project implements a computer model of sound propagation in the human thorax.
- project is based on article: [A high resolution computer model for sound propagation in the human thorax based on the Visible Human data set](https://www.sciencedirect.com/science/article/pii/S0010482503000441)



## Getting the data
Project uses computed tomography (CT) scan images from the [`Visible Human`](https://en.wikipedia.org/wiki/Visible_Human_Project) male data set.
- [`data download page`](https://mri.radiology.uiowa.edu/visible_human_datasets.html) 
- lungs images are in `Shoulder` region, this project use male dataset
- [`direct link for data archive`](https://mri.radiology.uiowa.edu/VHDicom/VHMCT1mm/VHMCT1mm_Shoulder.tar.gz)

This data is in [`DICOM`](https://en.wikipedia.org/wiki/DICOM) format. It need to be converted to `PNG` with 


---

Если конвертить в numpy arrany то min value во всем dataset = `0` max value = `3347`
Тоесть это как и говорят 12-bit image

Ну в numpy нет 12 bit, только: 
- `np.uint8` : `0-255`
- `np.uint16` : `0-65535` или `np.int16` : `-32768 to 32767`
- ну так как у меня там деление, всякие синусы будут - то мне нужно использовать float
    - ну для начала юзать `float64` - проверить для всех массивов max и min value - и соответственно понизить `float` (чтобы быстрее работало и памяти меньше). Если смогу уложиться в `np.float16` - вообще топ будет

- короче пока наверное downrate картинок сделать, потому что даже colab не вывозит `209 x 512 x 512` Есть варик в захода считать чтобы памяти хватило но хз

# походу ravel нужно юзать для скорости
```
The current API is that:

 - [`flatten`][1] always returns a copy.
 - [`ravel`][2] returns a view of the original array whenever possible. This isn't visible in the printed output, but if you modify the array returned by ravel, it may modify the entries in the original array. If you modify the entries in an array returned from flatten this will never happen. ravel will often be faster since no memory is copied, but you have to be more careful about modifying the array it returns.
 - [`reshape((-1,))`][3] gets a view whenever the strides of the array allow it even if that means you don't always get a contiguous array.


  [1]: https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.flatten.html
  [2]: https://docs.scipy.org/doc/numpy/reference/generated/numpy.ravel.html
  [3]: https://docs.scipy.org/doc/numpy/reference/generated/numpy.reshape.html
```

--- 

- `easy` Central Difference Method / Central differencing scheme
    - `easy` 7 point stencil
    - [scipy.misc.derivative — SciPy v0.15.1 Reference Guide](https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.misc.derivative.html)
    - [numpy.gradient — NumPy v1.14 Manual](https://docs.scipy.org/doc/numpy/reference/generated/numpy.gradient.html)
    - [numpy.diff — NumPy v1.14 Manual](https://docs.scipy.org/doc/numpy/reference/generated/numpy.diff.html)
- `hard` inhomogeneous wave equation + YT 
    - numerical solution
    - hyperbolic PDE
    - как я понял в моей задаче - heterogenous/nonhomogenous - когда среда /medium - неоднородная - тоесть takes into account the variation in density of the medium. Homogeneous - когда легкие одной плотности типа везде


Если че такой скрипт чтобы юзать cupy в colaboratory
```sh
!apt -y install libcusparse8.0 libnvrtc8.0 libnvtoolsext1
!ln -snf /usr/lib/x86_64-linux-gnu/libnvrtc-builtins.so.8.0 /usr/lib/x86_64-linux-gnu/libnvrtc-builtins.so
!pip install cupy-cuda80
```
