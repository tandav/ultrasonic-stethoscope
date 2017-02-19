using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;
using System.IO;
using RshCSharpWrapper;
using RshCSharpWrapper.RshDevice;

namespace forms_timer_label
{
    public partial class Form1 : Form
    {

        //Путь к каталогу, в который будет произведена запись данных.
        const string FILEPATH = "C:\\Users\\tandav\\Desktop\\data\\";

        //Служебное имя платы, с которой будет работать программа.
        const string BOARD_NAME = "LAn10_12USB";
        //Размер собираемого блока данных в отсчётах (на канал).
        //const uint BSIZE = 1048576;
        //const int BSIZE = 1048576;
        const int BSIZE = 65536;


        //Частота дискретизации. 
        const double SAMPLE_FREQ = 1.0e+8;

        //Создание экземляра класса для работы с устройствами
        Device device = new Device();

        //Код выполнения операции.
        RSH_API st;
        
        // Время ожидания(в миллисекундах) до наступления прерывания. Прерывание произойдет при полном заполнении буфера. 
        uint waitTime = 100000;
        uint loopNum = 0;

        //Структура для инициализации параметров работы устройства.  
        RshInitMemory p = new RshInitMemory();

        uint activeChanNumber = 0, serNum = 0;

        uint ticks = 0;
        Queue<double> adcQ; //
        List<double> moving_average = new List<double>(); // list with moving average values
        int mov_avg_window_size = 10000;
        int mov_avg_shift = 5000;
        List<double> prev_curr_buffer = Enumerable.Repeat(0.0, BSIZE * 2).ToList(); // buffer to store prev and curr buffer values filled with 0s


        public Form1()
        {
            InitializeComponent();
            numericUpDown1.Value = mov_avg_shift;
        }

        private void button1_Click(object sender, EventArgs e)
        {
            chart1.ChartAreas[0].AxisY.Minimum = -0.01;
            chart1.ChartAreas[0].AxisY.Maximum = 0.01;

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
            p.channels[0].gain = 1;

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

            timer1.Interval = 50;
            timer1.Start();
        }

        private void button2_Click(object sender, EventArgs e)
        {
            timer1.Stop();
            SayGoodBye(RSH_API.SUCCESS);
        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            st = device.Start(); // Запускаем плату на сбор буфера.
            if (st != RSH_API.SUCCESS) SayGoodBye(st);

            Console.WriteLine("\n--> Collecting buffer...\n", BOARD_NAME);

            if ((st = device.Get(RSH_GET.WAIT_BUFFER_READY_EVENT, ref waitTime)) == RSH_API.SUCCESS)    // Ожидаем готовность буфера.
            {
                Console.WriteLine("\nInterrupt has taken place!\nWhich means that onboard buffer had filled completely.");

                device.Stop();

                //Буфер с данными в мзр.
                short[] userBuffer = new short[p.bufferSize * activeChanNumber];
                //Буфер с данными в вольтах.
                double[] userBufferD = new double[p.bufferSize * activeChanNumber];

                //Получаем буфер с данными.
                st = device.GetData(userBuffer);
                if (st != RSH_API.SUCCESS) SayGoodBye(st);

                //Получаем буфер с данными. В этом буфере будут те же самые данные, но преобразованные в вольты.
                st = device.GetData(userBufferD);
                if (st != RSH_API.SUCCESS) SayGoodBye(st);

                //// Выведем в консоль данные в вольтах. (первые 10 измерений)
                //for (int i = 0; i < 10; i++)
                //    Console.WriteLine(userBufferD[i].ToString());


                prev_curr_buffer.RemoveRange(0, BSIZE);
                prev_curr_buffer.AddRange(userBufferD);

                moving_average.Clear();
                for (int i = BSIZE; i < 2 * BSIZE + 1; i += mov_avg_shift) // hard math, see pics for understanding
                    moving_average.Add(prev_curr_buffer.Skip(i - mov_avg_window_size + 1).Take(mov_avg_window_size).Sum() / mov_avg_window_size);


                label1.Text = "Ticks: " + ticks;
                ticks += 1;

                chart1.Series["Series1"].Points.DataBindY(moving_average);

                //// shame to remove
                //for (int i = 0; i < x_axis_points; i++) // TODO: fix that shame. (userbufferD is much bigger that x_axis_points)
                //{
                //    adcQ.Enqueue(userBufferD[i]);
                //    adcQ.Dequeue();
                //}

                //try
                //{
                //    chart1.Series["Series1"].Points.DataBindY(adcQ);
                //    //chart1.ResetAutoValues();
                //}
                //catch
                //{
                //    Console.WriteLine("No bytes recorded");
                //}
                //// end shame to remove

                //try // запись данных в файл
                //{
                //    string filePath = FILEPATH + BOARD_NAME + "_StartStop" + (++loopNum).ToString() + ".dat";
                //    WriteData(userBuffer, filePath);
                //    Console.WriteLine("\nData successfully collected and saved to {0}\nFile size: {1} kilobytes\n", filePath, (userBuffer.Length * sizeof(short)) / 1024);
                //}
                //catch (Exception ex)
                //{
                //    Console.WriteLine("Exception has happend! " + ex.Message);
                //}
            }
            else
                SayGoodBye(st);

            //label1.Text = counter.ToString();
            //counter += 1;
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

        private void numericUpDown1_ValueChanged(object sender, EventArgs e)
        {
            mov_avg_shift = Convert.ToInt32(numericUpDown1.Value);
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
    }
}
