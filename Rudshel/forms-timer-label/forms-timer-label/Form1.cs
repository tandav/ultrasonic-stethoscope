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

        //Внутренний объем блока данных.(внутренний буфер) Влияет на количество генерируемых прерываний в единицу времени.
        const uint BSIZE = 524288;
        //Фактически, от интенсивности генерируемых прерываний зависит производительность сбора.
        //Чем меньше прерываний, тем с большей вероятностью данные будут собраны без разрывов на высоких частотах.
        
        //Размер собираемого блока данных в отсчётах (на канал).
        //const uint BSIZE = 1048576;  //2^20
        //const int BSIZE = SAMPLE_FREQ / 1000 * timer_tick_interval;
        //const int BSIZE = 65536/2/2;

        //Количество внутренних буферов в конструируемом буфере данных.
        const uint IBUFCNT = 1;

        //const int SAMPLE_FREQ = 1048576*16;
        const int timer_tick_interval = 500;


        //Частота дискретизации. 
        const double SAMPLE_FREQ = 8.0e+7;
        // const int SAMPLE_FREQ = 100000000;  // SAMPLE_FREQ = 1000ms / timer_tick_interval * BSIZE

        int x_axis_points = 500;

        double[] values_to_draw;
        //Создание экземляра класса для работы с устройствами
        Device device = new Device();

        //Код выполнения операции.
        RSH_API st;

        //Структура для инициализации параметров работы устройства.  
        RshInitMemory p = new RshInitMemory();

        double r = 0.01;
        //List<double> buffer_list = new List<double>();
        int chart_updated_counter = 0;
        bool getting_data;

        double[] userBufferD;

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

            backgroundWorker1.ProgressChanged += backgroundWorker1_ProgressChanged;
            backgroundWorker1.WorkerReportsProgress = true;
            backgroundWorker1.WorkerSupportsCancellation = true;
        }

        private void button1_Click(object sender, EventArgs e)
        {
            values_to_draw = new double[x_axis_points];


            getting_data = true;
            backgroundWorker1.RunWorkerAsync();

            //timer1.Interval = timer_tick_interval;
            //timer1.Start();
        }

        private void button2_Click(object sender, EventArgs e)
        {
            backgroundWorker1.CancelAsync();
            getting_data = false;
            SayGoodBye(RSH_API.SUCCESS);
        }

        private void timer1_Tick(object sender, EventArgs e)
        {

            //for (int i = 0; i < buffer_list.Count; i++)
            //{
            //    if (i % buffer_list.Count / x_axis_points == 0)
            //    {
            //        chart1.Series["Series1"].Points.RemoveAt(0);
            //        chart1.Series["Series1"].Points.AddY(buffer_list[i]);
            //    }
            //}

            //List<double> buffer_list_draw = new List<double>();
            //for (int i = 0; i < buffer_list.Count; i++)
            //{
            //    if (i % buffer_list.Count / x_axis_points == 0)
            //    {
            //        buffer_list_draw.Add(buffer_list[i]);
            //    }
            //}
            //chart1.Series["Series1"].Points.DataBindY(buffer_list_draw);



            //label6.Text = (buffer_list.Count / BSIZE).ToString();

            //if (buffer_list.Count > 0)
            //{
            //}
            //buffer_list.Clear();
            //buffer_list_draw.Clear();
        }

        private void backgroundWorker1_DoWork(object sender, DoWorkEventArgs e)
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
            p.channels[0].gain = 10; // [1, 2, 5, 10] ~ [+-0.2V, +- 0.4V, +-1V, +- 2V] // probably inversed

            //Инициализация устройства (передача выбранных параметров сбора данных)
            //После инициализации неправильные значения в структуре будут откорректированы.
            st = device.Init(p);
            if (st != RSH_API.SUCCESS) SayGoodBye(st);

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

            //Буфер с "непрерывными" данными (для записи в файл).            
            userBufferD = new double[p.bufferSize * activeChanNumber * IBUFCNT];

            //Получаемый из платы буфер.
            double[] iBuffer = new double[p.bufferSize * activeChanNumber];


            //Время ожидания(в миллисекундах) до наступления прерывания. Прерывание произойдет при полном заполнении буфера. 
            uint waitTime = 100000; // default = 100000
            //uint loopNum = 0;



            int buffer_counter = 0;

            st = device.Start(); // Запускаем плату на сбор буфера.
            if (st != RSH_API.SUCCESS) SayGoodBye(st);

            while (getting_data)
            {
                for (int loop = 0; loop < IBUFCNT; loop++)
                {
                    //Console.WriteLine("\n--> Collecting buffer...\n", BOARD_NAME);
                    //Console.WriteLine("now before WAIT_BUFFER_READY_EVENT, loop = {0}", loop);

                    st = device.Get(RSH_GET.WAIT_BUFFER_READY_EVENT, ref waitTime);
                    if (st != RSH_API.SUCCESS) SayGoodBye(st);

                    //Console.WriteLine("succes at wait, loop = {0}", loop);


                    //Получаем буфер с данными. В этом буфере будут те же самые данные, но преобразованные в вольты.
                    st = device.GetData(iBuffer);
                    if (st != RSH_API.SUCCESS) SayGoodBye(st);


                    // Скопируем данные в "непрерывный" буфер.
                    iBuffer.CopyTo(userBufferD, loop * iBuffer.Length);

                    
                    //buffer_list.AddRange(userBufferD);
                    //buffers_storage.AddRange(userBufferD);
                }

                for (int i = 0, j = 0; i < userBufferD.Length; i++) // skip some values
                {
                    if (i % userBufferD.Length / x_axis_points == 0)
                    {
                        values_to_draw[j++] = userBufferD[i];
                    }
                }

                buffer_counter++;
                backgroundWorker1.ReportProgress(buffer_counter);
            }
            device.Stop(); // probably should del this (for full persistance)


        }

        private void backgroundWorker1_ProgressChanged(object sender, System.ComponentModel.ProgressChangedEventArgs e)
        {
            chart1.Series["Series1"].Points.DataBindY(values_to_draw);
            chart_updated_counter++;
            label4.Text = chart_updated_counter.ToString();
            // try update chart here
            label2.Text = e.ProgressPercentage.ToString();
        }

        private void numericUpDown1_ValueChanged(object sender, EventArgs e)
        {
            //x_axis_points = Convert.ToInt32(numericUpDown1.Value);
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
            Console.WriteLine(errorMessage + ", " + statusCode.ToString() + " ( 0x{0:x} ) ", (uint)statusCode);
            //Console.WriteLine("\n" + errorMessage);
            //Console.WriteLine("\n" + statusCode.ToString() + " ( 0x{0:x} ) ", (uint)statusCode);
            //Console.WriteLine("\n\nPress any key to end up the program.");
            //Console.WriteLine("Fatal error (SayGoodBye callback), you're fucked up! Stay cool!");
            return (int)statusCode;
        }
    }
}
