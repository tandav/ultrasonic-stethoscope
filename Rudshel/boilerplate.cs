/*!
 * \copyright 2016 JSC "Rudnev-Shilyaev"
 * 
 * \file LA-n10-12USB_StartStop.cs
 * \date 20.06.2016
 * 
 * \~english
 * \brief
 * Data acquisition in "Start-Stop" mode for LA-n10-12USB device
 * 
 * \~russian
 * \brief
 * Сбор данных в режиме "Старт-Стоп" для устройства ЛА-н10-12USB
 * 
 */


using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using RshCSharpWrapper;
using RshCSharpWrapper.RshDevice;


//################################# СБОР ДАННЫХ В РЕЖИМЕ СТАРТ-СТОП #################################

namespace StartStop
{
    class StartStop
    {

        static int Main(string[] args)
        {
            //Путь к каталогу, в который будет произведена запись данных.
            const string FILEPATH = "C:\\Users\\tandav\\Desktop\\data\\";

            //Служебное имя платы, с которой будет работать программа.
            const string BOARD_NAME = "LAn10_12USB";
            //Размер собираемого блока данных в отсчётах (на канал).
            const uint BSIZE = 1048576;
            //Частота дискретизации. 
            const double SAMPLE_FREQ = 1.0e+8;

            //Код выполнения операции.
            RSH_API st;

            //Создание экземляра класса для работы с устройствами
            Device device = new Device();

            //загрузка и подключение к библиотеке абстракции устройства
            st = device.EstablishDriverConnection(BOARD_NAME);
            if (st != RSH_API.SUCCESS) return SayGoodBye(st);

            Console.WriteLine("\n--> Start-Stop data acquisition mode <--\n\n");

            //=================== ИНФОРМАЦИЯ О ЗАГРУЖЕННОЙ БИБЛИОТЕКЕ ====================== 
            string libVersion, libname, libCoreVersion, libCoreName;

            st = device.Get(RSH_GET.LIBRARY_VERSION_STR, out libVersion);
            if (st != RSH_API.SUCCESS) return SayGoodBye(st);

            st = device.Get(RSH_GET.CORELIB_VERSION_STR, out libCoreVersion);
            st = device.Get(RSH_GET.CORELIB_FILENAME, out libCoreName);
            st = device.Get(RSH_GET.LIBRARY_FILENAME, out libname);

            Console.WriteLine("Library Name: {0:d}", libname);
            Console.WriteLine("Library Version: {0:d}", libVersion);
            Console.WriteLine("\nCore Library Name: {0:d}", libCoreName);
            Console.WriteLine("Core Library Version: {0:d}", libCoreVersion);

            //===================== ПРОВЕРКА СОВМЕСТИМОСТИ =================================  

            uint caps = (uint)RSH_CAPS.SOFT_GATHERING_IS_AVAILABLE;
            // Проверим, поддерживает ли плата функцию сбора данных в режиме "Старт-Стоп".
            st = device.Get(RSH_GET.DEVICE_IS_CAPABLE, ref caps);
            if (st != RSH_API.SUCCESS) return SayGoodBye(st);

            //========================== ИНИЦИАЛИЗАЦИЯ =====================================        

            //Подключаемся к устройству. Нумерация начинается с 1.
            st = device.Connect(1);
            if (st != RSH_API.SUCCESS) return SayGoodBye(st);

            /*
            Можно подключиться к устройству по заводскому номеру.
            uint serialNumber = 11111;
            st = device.Connect(serialNumber, RSH_CONNECT_MODE.SERIAL_NUMBER);
            if (st != RSH_API.SUCCESS) return SayGoodBye(st);
            */

            //Структура для инициализации параметров работы устройства.  
            RshInitMemory p = new RshInitMemory();
            //Запуск сбора данных программный. 
            p.startType = (uint)RshInitMemory.StartTypeBit.Program;
            //Размер внутреннего блока данных, по готовности которого произойдёт прерывание.
            p.bufferSize = BSIZE;
            //Частота дискретизации.
            p.frequency = SAMPLE_FREQ;

            //Сделаем 0-ой канал активным.
            p.channels[0].control = (uint)RshChannel.ControlBit.Used;
            //Зададим коэффициент усиления для 0-го канала.
            p.channels[0].gain = 1;

            //Инициализация устройства (передача выбранных параметров сбора данных)
            //После инициализации неправильные значения в структуре будут откорректированы.
            st = device.Init(p);
            if (st != RSH_API.SUCCESS) return SayGoodBye(st);

            //=================== ИНФОРМАЦИЯ О ПРЕДСТОЯЩЕМ СБОРЕ ДАННЫХ ====================== 

            uint activeChanNumber = 0, serNum = 0;
            device.Get(RSH_GET.DEVICE_ACTIVE_CHANNELS_NUMBER, ref activeChanNumber);
            device.Get(RSH_GET.DEVICE_NAME_VERBOSE, out libname);
            device.Get(RSH_GET.DEVICE_SERIAL_NUMBER, ref serNum);

            Console.WriteLine(
                "\nThe name of the connected device: {0} " +
                "\nSerial number of the connected device: {1:d} " +
                "\nData to be collected: {2:d} samples " +
                "\nADC frequency: {3:f} Hz " +
                "\nThe number of active channels: {4:d} " +
                "\nThe estimated time of gathering completion: {5:f} seconds",
                libname, serNum, p.bufferSize, p.frequency, activeChanNumber, (p.bufferSize / p.frequency));


            Console.WriteLine("\n=============================================================\n");

            // Время ожидания(в миллисекундах) до наступления прерывания. Прерывание произойдет при полном заполнении буфера. 
            uint waitTime = 100000;
            uint loopNum = 0;

            do // Алгоритм сбора данных в режиме Старт-Стоп.
            {
                Console.WriteLine("\n\nPress Esc key to exit, any other key to start {0} ...\n\n", BOARD_NAME);

                if (Console.ReadKey().Key == ConsoleKey.Escape) break;

                st = device.Start(); // Запускаем плату на сбор буфера.
                if (st != RSH_API.SUCCESS) return SayGoodBye(st);

                Console.WriteLine("\n--> Collecting buffer...\n", BOARD_NAME);

                if ((st = device.Get(RSH_GET.WAIT_BUFFER_READY_EVENT, ref waitTime)) == RSH_API.SUCCESS)	// Ожидаем готовность буфера.
                {
                    Console.WriteLine("\nInterrupt has taken place!\nWhich means that onboard buffer had filled completely.");

                    device.Stop();

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

                    // Выведем в консоль данные в вольтах. (первые 10 измерений)
                    for (int i = 0; i < 10; i++)
                        Console.WriteLine(userBufferD[i].ToString());


                    try // запись данных в файл
                    {
                        string filePath = FILEPATH + BOARD_NAME + "_StartStop" + (++loopNum).ToString() + ".dat";
                        WriteData(userBuffer, filePath);
                        Console.WriteLine("\nData successfully collected and saved to {0}\nFile size: {1} kilobytes\n", filePath, (userBuffer.Length * sizeof(short)) / 1024);
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine("Exception has happend! " + ex.Message);
                    }
                }
                else
                    return SayGoodBye(st);

            } while (true);

            return SayGoodBye(RSH_API.SUCCESS);
        }


        static void WriteData(short[] values, string path)
        {
            using (FileStream fs = new FileStream(path, FileMode.OpenOrCreate, FileAccess.Write))
            {
                using (BinaryWriter bw = new BinaryWriter(fs))
                {
                    foreach (short value in values)
                    {
                        bw.Write(value);
                    }
                }
            }
        }

        public static int SayGoodBye(RSH_API statusCode)
        {
            string errorMessage;
            Device.RshGetErrorDescription(statusCode, out errorMessage, RSH_LANGUAGE.RUSSIAN);
            Console.WriteLine("\n" + errorMessage);
            Console.WriteLine("\n" + statusCode.ToString() + " ( 0x{0:x} ) ", (uint)statusCode);
            Console.WriteLine("\n\nPress any key to end up the program.");
            Console.ReadKey();
            return (int)statusCode;
        }

    }
}
