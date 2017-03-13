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
        const uint   BSIZE          = 524288;                               //буфер, количество значений, собираемых за раз. Чем реже обращаешься тем лучше (чем больше буффер)
        const double RATE           = 8.0e+7;                               //Частота дискретизации. 
        const int block_size        = 10;
        int x_axis_points           = 20000;

        double[] block; // block of buffers (see pic for explanation)
        double[] values_to_draw;
        Device device = new Device(); //Создание экземляра класса для работы с устройствами
        RSH_API st; //Код выполнения операции.
        RshInitMemory p = new RshInitMemory(); //Структура для инициализации параметров работы устройства. 
        double r = 0.01; // chart Y-axis bounds
        bool getting_data;
        long series_dt = 0;
        Stopwatch stopwatch = new Stopwatch();
        Stopwatch stopwatch2 = new Stopwatch(); // need second stopwatch 'cause they works async

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
        }

        private void button2_Click(object sender, EventArgs e)
        {
            backgroundWorker1.CancelAsync();
            getting_data = false;
            SayGoodBye(RSH_API.SUCCESS);
        }

        private void backgroundWorker1_DoWork(object sender, DoWorkEventArgs e)
        {
            //========================== ИНИЦИАЛИЗАЦИЯ =====================================        
            st = device.EstablishDriverConnection(BOARD_NAME); //загрузка и подключение к библиотеке абстракции устройства
            if (st != RSH_API.SUCCESS) SayGoodBye(st);
            st  = device.Connect(1); //Подключаемся к устройству. Нумерация начинается с 1.
            if (st != RSH_API.SUCCESS) SayGoodBye(st);
            p.startType           = (uint)RshInitMemory.StartTypeBit.Program; //Запуск сбора данных программный. 
            p.bufferSize          = BSIZE; //Размер внутреннего блока данных, по готовности которого произойдёт прерывание.
            p.frequency           = RATE;  //Частота дискретизации.
            p.channels[0].control = (uint)RshChannel.ControlBit.Used;  //Сделаем 0-ой канал активным.
            p.channels[0].gain    = 10; // коэффициент усиления для 0-го канала. [1, 2, 5, 10] ~ [+-0.2V, +- 0.4V, +-1V, +- 2V] // probably inversed
            st = device.Init(p); //Инициализация устройства (передача выбранных параметров сбора данных)
            if (st != RSH_API.SUCCESS) SayGoodBye(st); //После инициализации неправильные значения в структуре будут откорректированы.

            double[] buffer = new double[p.bufferSize]; //Получаемый из платы буфер.
            //block = new double[p.bufferSize * block_size];
            block = new double[block_size];


            
            //Время ожидания(в миллисекундах) до наступления прерывания. Прерывание произойдет при полном заполнении буфера. 
            uint waitTime = 100000; // default = 100000
            //uint loopNum = 0;
            int block_counter = 0; // counts the series of buffer arrays

            while (getting_data)
            {
                stopwatch.Restart();
                st = device.Start(); // Запускаем плату на сбор буфера.
                if (st != RSH_API.SUCCESS) SayGoodBye(st);

                for (int i = 0; i < block_size; i++) // Series of buffers
                {
                    st = device.Get(RSH_GET.WAIT_BUFFER_READY_EVENT, ref waitTime);
                    if (st != RSH_API.SUCCESS) SayGoodBye(st);

                    st = device.GetData(buffer); // very big amount of data
                    if (st != RSH_API.SUCCESS) SayGoodBye(st);
                    device.Stop();

                    //values_to_draw[i] = buffer.Average();
                    double sum = 0;
                    for (int k = 0; k < 5; k++) // rough average
                        sum += buffer[BSIZE / 5 * k] / 5;
                    block[i] = sum;

                    //buffer.CopyTo(block, i * buffer.Length);
                }

                double[] values_to_draw_copy = (double[])values_to_draw.Clone();

                for (int i = 0; i < x_axis_points - block_size; i++) // Queue Dequeue and Enqueue implementation with arrays
                {
                    values_to_draw[i] = values_to_draw_copy[block_size + i];
                }

                for (int i = 0; i < block_size; i++)
                {
                    values_to_draw[x_axis_points - block_size + i] = block[i];
                }

                //for (int i = 0; i < block_size; i++)
                //{
                //    values_to_draw.Dequeue();
                //    values_to_draw.Enqueue(block[i]);
                //}

                //for (int i = 0, j = 0; i < block.Length; i++) // skip some values
                //{
                //    if (i % buffer.Length / x_axis_points == 0 && j < values_to_draw.Length)
                //    {
                //        values_to_draw[j++] = block[i];
                //    }
                //    block[i] = 0; // cleaning
                //}
                block_counter++;
                stopwatch.Stop();
                series_dt = stopwatch.ElapsedMilliseconds;
                backgroundWorker1.ReportProgress(block_counter);
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
            r /= 2;
            chart1.ChartAreas[0].AxisY.Minimum = -r;
            chart1.ChartAreas[0].AxisY.Maximum = r;
        }

        private void button3_Click(object sender, EventArgs e)
        {
            r *= 2;
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
