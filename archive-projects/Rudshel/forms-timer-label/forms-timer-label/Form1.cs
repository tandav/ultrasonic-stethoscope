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
        const string BOARD_NAME         = "LAn10_12USB";
        const uint   BSIZE              = 524288;        //буфер, количество значений, собираемых за раз. Чем реже обращаешься тем лучше (чем больше буффер)
        const double RATE               = 8.0e+7;
        const int    buffers_per_x_axis = 20;
        const int    r_buffers_in_block = 5;  // number of reduced buffers in block
        const int    x_axis_points      = 21000;
        int          r_buffer_size      = x_axis_points / buffers_per_x_axis;          

        double[] block;
        double[] values_to_draw;
        Device device = new Device(); //Создание экземляра класса для работы с устройствами
        RSH_API st; //Код выполнения операции.
        RshInitMemory p = new RshInitMemory(); //Структура для инициализации параметров работы устройства. 
        double r = 0.01; // chart Y-axis bounds
        bool getting_data;
        Stopwatch stopwatch = new Stopwatch();
        Stopwatch stopwatch2 = new Stopwatch(); // need second stopwatch 'cause they works async

        public Form1()
        {
            InitializeComponent();
            numericUpDown1.Value = x_axis_points;
            values_to_draw = new double[x_axis_points];
            

            chart1.ChartAreas[0].AxisY.Minimum = -r;
            chart1.ChartAreas[0].AxisY.Maximum = r;
            
            for (int i = 0; i < x_axis_points; i++)
            {
                chart1.Series["Series1"].Points.AddY(0);
            }

            backgroundWorker1.WorkerSupportsCancellation = true;
        }

        private void button1_Click(object sender, EventArgs e)
        {
            if (button1.Text == "Start")
            {
                getting_data = true;
                button1.Text = "Stop";
                button1.BackColor = System.Drawing.Color.Tomato;
                backgroundWorker1.RunWorkerAsync();
                timer1.Interval = 100;
                timer1.Start();
            }
            else
            {
                backgroundWorker1.CancelAsync();
                getting_data = false;
                SayGoodBye(RSH_API.SUCCESS);
                button1.Text = "Start";
                button1.BackColor = System.Drawing.Color.PaleGreen;
            }

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
            uint waitTime = 100000; // Время ожидания(в миллисекундах) до наступления прерывания. Прерывание произойдет при полном заполнении буфера.  // default = 100000
            while (getting_data)
            {
                stopwatch.Restart();

                st = device.Start(); // Запускаем плату на сбор буфера. по идее нужно для каждого буффера start-stop (в цикле for) Но вроде и так работает и так быстрее намного. (Типа старт за циклом, стоп - внутри for; оба за циклом - не работуют)
                if (st != RSH_API.SUCCESS) SayGoodBye(st);

                st = device.Get(RSH_GET.WAIT_BUFFER_READY_EVENT, ref waitTime);
                if (st != RSH_API.SUCCESS) SayGoodBye(st);

                st = device.GetData(buffer); // very big amount of data
                if (st != RSH_API.SUCCESS) SayGoodBye(st);

                device.Stop();

                // Queue Dequeue and Enqueue implementation with arrays
                double[] values_to_draw_copy = (double[])values_to_draw.Clone();
                for (int i = 0; i < x_axis_points - r_buffer_size; i++) 
                    values_to_draw[i] = values_to_draw_copy[r_buffer_size + i];

                for (int i = 0; i < r_buffer_size; i++)
                    values_to_draw[x_axis_points - r_buffer_size + i] = buffer[BSIZE / r_buffer_size * i];

                stopwatch.Stop();
                Console.WriteLine("GetData() time:\t" + stopwatch.ElapsedMilliseconds + "ms");
            }
        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            stopwatch2.Restart();
            chart1.Series[0].Points.DataBindY(values_to_draw);
            stopwatch2.Stop();
            Console.WriteLine("Redraw time:\t\t" + stopwatch2.ElapsedMilliseconds + "ms");
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
