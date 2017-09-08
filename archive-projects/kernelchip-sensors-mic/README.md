# Kernel Chip Temperature [Deprecated]

## Outline
1. Первый pin - как выход
2. Типа 0 на пине - первый датчик, 1 - второй термодатчик
2. Считывать данный (ну аля от 0 до 1023) с АЦП

## Linux Setup

Name of chip is `/dev/tty.usbmodem1411` Plug, Unplyg and check name with `ls /dev/tty.*` Там просто при переподключении немного меняется имя

Чтобы открыть терминал кернел чипа:
`screen /dev/tty.usbmodem1411`

Но он короче не отзывается

[Hidden Features of `screen` - Server Fault](http://serverfault.com/questions/81544/hidden-features-of-screen/81548#81548)


Google some like [serial port mac terminal - Google Search](https://www.google.ru/search?q=serial+port+mac+terminal&oq=serial+port+mac&aqs=chrome.1.69i57j0l5.7968j0j7&sourceid=chrome&ie=UTF-8)

[Manufacturer site](http://www.kernelchip.ru/Ke-USB24A.php)


- [osx - How to find the serial port number on Mac OS X? - Stack Overflow](http://stackoverflow.com/questions/12254378/how-to-find-the-serial-port-number-on-mac-os-x)