using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;
using System.IO;
using RshCSharpWrapper;
using RshCSharpWrapper.RshDevice;
using System.ComponentModel;
using System.Diagnostics;

namespace forms_timer_label
{
    public partial class Form1 : Form
    {
        const string FILEPATH       = "C:\\Users\\tandav\\Desktop\\data\\"; //Путь к каталогу, в который будет произведена запись данных.
        const string BOARD_NAME     = "LAn10_12USB";                        //Служебное имя платы, с которой будет работать программа.
        const uint   BSIZE          = 524288;                               // буфер, количество значений, собираемых за раз. Чем реже обращаешься тем лучше (чем больше буффер)
        const double SAMPLE_FREQ    = 8.0e+7;                               //Частота дискретизации. 
        const int buffers_in_series = 100;                                   //Количество внутренних буферов в конструируемом буфере данных.
        int x_axis_points           = 200;

        double[] values_to_draw;
        Device device = new Device(); //Создание экземляра класса для работы с устройствами
        RSH_API st; //Код выполнения операции.
        RshInitMemory p = new RshInitMemory(); //Структура для инициализации параметров работы устройства. 
        double r = 0.01;
        //List<double> buffer_list = new List<double>();
        int chart_updated_counter = 0;
        bool getting_data;
        double[] buffer_array;
        long series_dt = 0;
        Stopwatch stopwatch = new Stopwatch();
        Stopwatch stopwatch2 = new Stopwatch(); // need second stopwatch 'cause they works async

        //Stopwatch stopwatch = Stopwatch.StartNew();


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
            // DEL THIS?
            st = device.EstablishDriverConnection(BOARD_NAME); //загрузка и подключение к библиотеке абстракции устройства
            if (st != RSH_API.SUCCESS) SayGoodBye(st);

            //========================== ИНИЦИАЛИЗАЦИЯ =====================================        

            st = device.Connect(1); //Подключаемся к устройству. Нумерация начинается с 1.
            if (st != RSH_API.SUCCESS) SayGoodBye(st);
           
            p.startType = (uint)RshInitMemory.StartTypeBit.Program; //Запуск сбора данных программный. 
            p.bufferSize = BSIZE; //Размер внутреннего блока данных, по готовности которого произойдёт прерывание.
            p.frequency = SAMPLE_FREQ;  //Частота дискретизации.
            p.channels[0].control = (uint)RshChannel.ControlBit.Used;  //Сделаем 0-ой канал активным.
            p.channels[0].gain = 10; // //Зададим коэффициент усиления для 0-го канала. [1, 2, 5, 10] ~ [+-0.2V, +- 0.4V, +-1V, +- 2V] // probably inversed

            //Инициализация устройства (передача выбранных параметров сбора данных)
            //После инициализации неправильные значения в структуре будут откорректированы.
            st = device.Init(p);
            if (st != RSH_API.SUCCESS) SayGoodBye(st);


                      
            double[] buffer = new double[p.bufferSize]; //Получаемый из платы буфер.
            //buffer_array = new double[p.bufferSize * buffers_in_series];


            //Время ожидания(в миллисекундах) до наступления прерывания. Прерывание произойдет при полном заполнении буфера. 
            uint waitTime = 100000; // default = 100000
            //uint loopNum = 0;
            int buffer_array_counter = 0; // counts the series of buffer arrays

            while (getting_data)
            {
                stopwatch.Restart();
                st = device.Start(); // Запускаем плату на сбор буфера.
                if (st != RSH_API.SUCCESS) SayGoodBye(st);

                for (int i = 0, j = 0; i < buffers_in_series; i++) // Series of buffers
                {
                    st = device.Get(RSH_GET.WAIT_BUFFER_READY_EVENT, ref waitTime);
                    if (st != RSH_API.SUCCESS) SayGoodBye(st);

                    st = device.GetData(buffer); // very big amount of data
                    if (st != RSH_API.SUCCESS) SayGoodBye(st);
                    device.Stop();

                    values_to_draw[i] = buffer.Average();
                    //if (i  == 0 && j < x_axis_points)
                    //{
                    //    values_to_draw[j++] = buffer[0];
                    //}
                    //reduce(buffer, x_axis_points / buffers_in_series).CopyTo(values_to_draw, i * x_axis_points / buffers_in_series); // reducing that shit
                    //buffer.CopyTo(buffer_array, i * buffer.Length);
                }

                //for (int i = 0, j = 0; i < buffer_array.Length; i++) // skip some values
                //{
                //    if (i % buffer.Length / x_axis_points == 0 && j < values_to_draw.Length)
                //    {
                //        values_to_draw[j++] = buffer_array[i];
                //    }
                //    buffer_array[i] = 0; // cleaning
                //}
                buffer_array_counter++;
                stopwatch.Stop();
                series_dt = stopwatch.ElapsedMilliseconds;
                backgroundWorker1.ReportProgress(buffer_array_counter);
            }
        }

        private void backgroundWorker1_ProgressChanged(object sender, System.ComponentModel.ProgressChangedEventArgs e)
        {
            stopwatch2.Restart();
            Console.Write("Get-data time:\t" + series_dt + "ms\t\t");
            chart1.Series[0].Points.DataBindY(values_to_draw);
            label2.Text = e.ProgressPercentage.ToString();
            stopwatch2.Stop();
            Console.Write("Redraw and log time:\t" + stopwatch.ElapsedMilliseconds + "ms\n");


            // try update chart here
            //label4.Text = stopwatch.ElapsedMilliseconds.ToString();
            //label4.Text = stopwatch.ElapsedMilliseconds.ToString();

        }

        private double[] reduce(double[] array, int array_out_length)
        {
            double[] array_out = new double[array_out_length];
            for (int i = 0, j = 0; i < array.Length; i++)
            {
                if (i % array.Length / array_out_length == 0)
                {
                    array_out[j++] = array[i];
                }
            }
            return array_out;
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
