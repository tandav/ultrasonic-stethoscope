это не (У) версия. Тоесть более стремная.

---
Частота дискретезации - юзать `double` // хотя мб и пофиг, но по дефолту это дабл, хз что быстрее

```cs
MIN_FREQUENCY     = 1250000;
MAX_FREQUENCY     = 80000000; // 8.0e+7
MAX_BUFFER_SIZE   = 524288;   // = 2^19 уверенность 90%
12 разрядов: 2^12 = 4096 значений по вертикали.
```

---
чтобы получить списки допустимых значений (буфферы) - можно программу на .cpp запустить, просто там есть готовые примеры, в отличие от c#

---

## Rudshel ADC Stuff
![adc](https://cloud.githubusercontent.com/assets/5549677/24586244/890d0614-17a4-11e7-9e1c-1547d653e5aa.png)

[Measurement table on google spreadsheets](https://docs.google.com/spreadsheets/d/19mu0-q33grOXhcmliKezvnzJJl0XOe1p6kiq_wnQhLg/edit?usp=sharing)

---
When work with Rudshell API, make sure to put dll in bin/Debug folder. Как бы колхоз, но пока пока нет времени разбираться, как нормально ссылку на dll сделать. (ну я пытался часа 2, но ain succes)

---
Когда юзаешь `short` - данные придут в мзр, когда `double` - в вольтах. ([отсюда](http://www.rudshel.ru/soft/SDK2/Doc/CPP_USER_RU/html/struct_i_rsh_device.html#a5fe82265d052163e34a1ffab4fec1c6d))
```cs
//Буфер с данными в мзр.
short[] userBuffer = new short[p.bufferSize * activeChanNumber]; 
//Буфер с данными в вольтах.
double[] userBufferD = new double[p.bufferSize * activeChanNumber]; 

//Получаем буфер с данными.
st = device.GetData(userBuffer);	
if (st != RSH_API.SUCCESS) return SayGoodBye(st);
//Получаем буфер с данными. В этом буфере будут те же самые данные, но преобразованные в вольты.
st = device.GetData(userBufferD);	
if (st != RSH_API.SUCCESS) return SayGoodBye(st);
```

---

MIND = BLOWN, Enlightenment

This ADC is not capable of persistent data acquisition mode. Теперь понятно, почему все так стремно работало. По сути нужно каждый раз делать start / stop. So there will be artifacts in signal waveform.

![is-capable-of-persistent-mode](https://cloud.githubusercontent.com/assets/5549677/23857660/08bfad8a-080f-11e7-85a7-018390d1c680.PNG)

---

Когда делаешь такие запросы инфы - смотри чтобы переменная куда пишешь была нужного типа (`string, int, uint` - смотри в документации)

```cs
string libname;
st = device.Get(RSH_GET.LIBRARY_FILENAME, out libname);
Console.WriteLine("Library Name: {0:d}", libname);
```

Плюс там такие варики иногда бывают `uint caps = (uint)RSH_CAPS.SOFT_GATHERING_IS_AVAILABLE;`

---

### call to manufacturer

- у меня АЦП ЛАн10-12USB(-У)
- Я запустил программу из документации (с сайта, там есть примеры на C#)

---

- Он работает в режиме старт-стоп, типа запуск, сбор данных, стоп. И так в цикле, сколько угодно раз
- Ну у меня как бы бесконечный цикл, просто подряд он старт-сбор-данных-стоп

---

- Я засек время одного цикла сбора
- У меня максимальная частота дискретизации и максимальный буффер для этого ацп (80МГц и 2^19 отсчетов в буффере)
- у меня получилось 190 мс
  - как бы он не все это время собирает данные. 
  - можно посчитать из пропорции сколько милисекунд занимает идеальный сбор данных 
    - (когда он 100% собирает данные и не тратит время на перезапуск)
  - Ну, частота дискретизации - это сколько отсчетов за 1секунду (тоесть за `1000мс`)
  - Ну частота дискр 80МГц, тоесть `80 млн` отсчетов за `1000мс`
  - буффер отсчетов(`2^19`) - за `Х` секунд
  - отсюда время за которое в идеале должен собираться буффер `2^19 * 1000 / 80млн = ~6.5мс`
- ну а он собирается за 190 мс
- тоесть почти все время тратится на перезапуск. 
  - и суть в том что типа 6.5 мс он собирает данные, потом перезапускается 180 мс.
  - большая часть данных теряется

- вобщем вопрос, возможно я не правильно использую, и нормально ли это для этого ацп, мб по другому как-то нужно. 
---


### Links
- [Rsh API: Документация по программированию устройств ЗАО "Руднев-Шиляев"](http://www.rudshel.ru/soft/SDK2/Doc/CPP_USER_RU/html/index.html)
- [ADC ЛА-н10-12USB](http://www.rudshel.ru/show.php?dev=14)
- [Rudshel ADC Docs [PDF]](https://www.dropbox.com/s/a6uxxe81noef8vm/LA-n10-12USB%28y%29.pdf?dl=0)
