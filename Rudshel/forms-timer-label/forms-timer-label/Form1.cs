using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;
using System.IO;
using RshCSharpWrapper;
using RshCSharpWrapper.RshDevice;
using System.ComponentModel;

namespace forms_timer_label
{
    public partial class Form1 : Form
    {
        //Путь к каталогу, в который будет произведена запись данных.
        const string FILEPATH = "C:\\Users\\tandav\\Desktop\\data\\";

        //Служебное имя платы, с которой будет работать программа.
        const string BOARD_NAME = "LAn10_12USB";
        const int SAMPLE_FREQ = 10000000;
        const int timer_tick_interval = 10;
        int x_axis_points = 1000;
        //Размер собираемого блока данных в отсчётах (на канал).
        //const uint BSIZE = 1048576;
        const int BSIZE = SAMPLE_FREQ /1000*timer_tick_interval;
        //const int BSIZE = 65536/2/2;

        //Частота дискретизации. 
        //const double SAMPLE_FREQ = 1.0e+8;
        // const int SAMPLE_FREQ = 100000000;  // SAMPLE_FREQ = 1000ms / timer_tick_interval * BSIZE


        //Создание экземляра класса для работы с устройствами
        Device device = new Device();

        //Код выполнения операции.
        RSH_API st;

        //Структура для инициализации параметров работы устройства.  
        RshInitMemory p = new RshInitMemory();

        uint activeChanNumber = 0, serNum = 0;
        Random random = new Random();
        double[] rand_array = new double[BSIZE];
        // Время ожидания(в миллисекундах) до наступления прерывания. Прерывание произойдет при полном заполнении буфера. 
        uint waitTime = 100000;
        double r = 0.01;
        int skip_ratio = 1000;
        //List<double> buffers_storage = Enumerable.Repeat(0.0, BSIZE * 10).ToList();
        List<double> buffers_storage = new List<double>();

        //Буфер с данными в мзр. // TODO: del this
        //short[] userBuffer = new short[p.bufferSize * activeChanNumber];
        //Буфер с данными в вольтах.
        double[] userBufferD = new double[BSIZE];

        public Form1()
        {
            InitializeComponent();
            numericUpDown1.Value = x_axis_points;

            chart1.ChartAreas[0].AxisY.Minimum = -r;
            chart1.ChartAreas[0].AxisY.Maximum = r;
            for (int i = 0; i < x_axis_points; i++)
            {
                chart1.Series["Series1"].Points.AddY(0);
            }
        }

 

        private void button1_Click(object sender, EventArgs e)
        {
            // Some Initialisation Work

            //загрузка и подключение к библиотеке абстракции устройства
            st = device.EstablishDriverConnection(BOARD_NAME);
            if (st != RSH_API.SUCCESS) SayGoodBye(st);

            Console.WriteLine("\n--> Start-Stop data acquisition mode <--\n\n");

            //=================== ИНФОРМАЦИЯ О ЗАГРУЖЕННОЙ БИБЛИОТЕКЕ ====================== 
            string libVersion, libname, libCoreVersion, libCoreName;

            st = device.Get(RSH_GET.LIBRARY_VERSION_STR, out libVersion);
            if (st != RSH_API.SUCCESS) SayGoodBye(st);

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
            if (st != RSH_API.SUCCESS) SayGoodBye(st);

            //========================== ИНИЦИАЛИЗАЦИЯ =====================================        

            //Подключаемся к устройству. Нумерация начинается с 1.
            st = device.Connect(1);
            if (st != RSH_API.SUCCESS) SayGoodBye(st);

            /*
            Можно подключиться к устройству по заводскому номеру.
            uint serialNumber = 11111;
            st = device.Connect(serialNumber, RSH_CONNECT_MODE.SERIAL_NUMBER);
            if (st != RSH_API.SUCCESS) return SayGoodBye(st);
            */


            //Запуск сбора данных программный. 
            p.startType = (uint)RshInitMemory.StartTypeBit.Program;
            //Размер внутреннего блока данных, по готовности которого произойдёт прерывание.
            p.bufferSize = BSIZE;
            //Частота дискретизации.
            p.frequency = SAMPLE_FREQ;

            //Сделаем 0-ой канал активным.
            p.channels[0].control = (uint)RshChannel.ControlBit.Used;
            //Зададим коэффициент усиления для 0-го канала.
            p.channels[0].gain = 10; // [1, 2, 5, 10] ~ [+-0.2V, +- 0.4V, +-1V, +- 2V]

            //Инициализация устройства (передача выбранных параметров сбора данных)
            //После инициализации неправильные значения в структуре будут откорректированы.
            st = device.Init(p);
            if (st != RSH_API.SUCCESS) SayGoodBye(st);

            //=================== ИНФОРМАЦИЯ О ПРЕДСТОЯЩЕМ СБОРЕ ДАННЫХ ====================== 

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


            timer1.Interval = timer_tick_interval;
            timer1.Start();

            //timer2.Interval = 100;
            //timer2.Start();

            //chart1.Series["Series1"].Points.DataBindY(userBufferD);

        }

        private void button2_Click(object sender, EventArgs e)
        {
            SayGoodBye(RSH_API.SUCCESS);
        }

        private void numericUpDown1_ValueChanged(object sender, EventArgs e)
        {
            x_axis_points = Convert.ToInt32(numericUpDown1.Value);
        }

        public static int SayGoodBye(RSH_API statusCode)
        {
            string errorMessage;
            Device.RshGetErrorDescription(statusCode, out errorMessage, RSH_LANGUAGE.RUSSIAN);
            Console.WriteLine("\n" + errorMessage);
            Console.WriteLine("\n" + statusCode.ToString() + " ( 0x{0:x} ) ", (uint)statusCode);
            Console.WriteLine("\n\nPress any key to end up the program.");
            //Console.ReadKey();
            return (int)statusCode;
        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            st = device.Start(); // Запускаем плату на сбор буфера.
            if (st != RSH_API.SUCCESS) SayGoodBye(st);

            //Console.WriteLine("\n--> Collecting buffer...\n", BOARD_NAME);

            if ((st = device.Get(RSH_GET.WAIT_BUFFER_READY_EVENT, ref waitTime)) == RSH_API.SUCCESS)    // Ожидаем готовность буфера.
            {
                //Console.WriteLine("\nInterrupt has taken place!\nWhich means that onboard buffer had filled completely.");

                device.Stop(); // TODO: Maybe del this



                //Получаем буфер с данными. // TODO: del this
                //st = device.GetData(userBuffer);
                //if (st != RSH_API.SUCCESS) SayGoodBye(st);

                //Получаем буфер с данными. В этом буфере будут те же самые данные, но преобразованные в вольты.
                st = device.GetData(userBufferD);
                if (st != RSH_API.SUCCESS) SayGoodBye(st);
                //buffers_storage.AddRange(userBufferD);

                for (int i = 0; i < userBufferD.Length; i++)
                {
                    if (i % 100 == 0)
                    {
                        chart1.Series["Series1"].Points.RemoveAt(0);
                        chart1.Series["Series1"].Points.AddY(userBufferD[i]);
                    }

                }
            }
        }

        private void button4_Click(object sender, EventArgs e)
        {
            r /= 10;
            chart1.ChartAreas[0].AxisY.Minimum = -r;
            chart1.ChartAreas[0].AxisY.Maximum = r;
        }

        private void button3_Click(object sender, EventArgs e)
        {
            r *= 10;
            chart1.ChartAreas[0].AxisY.Minimum = -r;
            chart1.ChartAreas[0].AxisY.Maximum = r;
        }

        private void timer2_Tick(object sender, EventArgs e)
        {
            //List<double> buffers_storage_copy = new List<double>();
            //for (int i = 0; i < buffers_storage.Count; i++)
            //{
            //    if (i % buffers_storage.Count / x_axis_points == 0) // draw only each 1000th data point (for better performance)
            //    {
            //        buffers_storage_copy.Add(buffers_storage[i]);
            //    }
            //}

            ////chart1.Series["Series1"].Points.RemoveAt(0);
            ////chart1.Series["Series1"].Points.AddY(userBufferD[i]);
            ////chart1.Series["Series1"].Points.DataBindY(userBufferD);

            //buffers_storage.Clear();
            //buffers_storage_copy.Clear();

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
    }
}
