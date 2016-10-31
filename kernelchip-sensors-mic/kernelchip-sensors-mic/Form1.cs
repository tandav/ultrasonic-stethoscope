using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;
using NAudio.Wave;
using System.IO.Ports;

namespace kernelchip_sensors_mic
{
    public partial class Form1 : Form
    {
        //mic
        int n_mic = 4000; //number of x-axis points
        WaveIn wi;
        Queue<int> mic_Q;

        //sensors
        SerialPort serialPort1;
        int n_sensors = 400; // number of x-axis points
        Queue<int> sensor1_Q; // make int?
        Queue<int> sensor2_Q; // make int?
        
        //Stopwatch time = new Stopwatch();

        public Form1()
        {
            InitializeComponent();
        }


        private void Form1_Load(object sender, EventArgs e)
        {
            //mic
            //also uncoment in draw_charts()
            mic_Q = new Queue<int>(Enumerable.Repeat(0, n_mic).ToList()); // fill mic_Q w/ zeros
            chart1.ChartAreas[0].AxisY.Minimum = -2500;
            chart1.ChartAreas[0].AxisY.Maximum = 2500;
            wi = new WaveIn();
            wi.StartRecording();
            wi.WaveFormat = new WaveFormat(44100, 16, 1);
            wi.DataAvailable += new EventHandler<WaveInEventArgs>(wi_DataAvailable);
            timer1.Enabled = true;

            //time.Start();

            //sensors
            sensor1_Q = new Queue<int>(Enumerable.Repeat(0, n_sensors).ToList()); // fill w/ zeros
            sensor2_Q = new Queue<int>(Enumerable.Repeat(0, n_sensors).ToList()); // fill w/ zeros

            int chart_radius = 1000;

            chart2.ChartAreas[0].AxisY.Minimum = -chart_radius;
            chart2.ChartAreas[0].AxisY.Maximum = chart_radius;

            chart3.ChartAreas[0].AxisY.Minimum = -chart_radius;
            chart3.ChartAreas[0].AxisY.Maximum = chart_radius;

            serialPort1 = new SerialPort();
            serialPort1.ReadTimeout = 100; // default=50
            serialPort1.WriteTimeout = 100; // default=50
            if (SearchKeUSB())
            {
                WriteRead("$KE,IO,SET,1,0,S"); // set 1st pin as out
                timer1.Enabled = true;
            }
            else label1.Text = "Error: Can't connect to Kernel Chip";
        }

        void draw_charts()
        {
            try { chart1.Series["Mic"].Points.DataBindY(mic_Q); }
            catch { Console.WriteLine("No bytes recorded"); }

            chart2.Series["Sensor1"].Points.DataBindY(sensor1_Q);
            chart3.Series["Sensor2"].Points.DataBindY(sensor2_Q);
        }

        string WriteRead(string requiry)
        {
            requiry += System.Environment.NewLine;
            serialPort1.Write(requiry);

            string message; //returned message from kernelchip
            try
            {
                message = serialPort1.ReadLine();
                return message;
            }
            catch (TimeoutException)
            {
                return "err-cannot write/read";
            }
        }

        bool SearchKeUSB() // maybe too complex, but vrode norm
        {
            string[] ports = SerialPort.GetPortNames();
            for (int i = 0; i < ports.Length; i++)
            {
                serialPort1.PortName = ports[i];
                try
                {
                    serialPort1.Open();
                    if (WriteRead("$KE").Substring(0, 3) == "#OK") break;
                }
                catch
                {
                    return false;
                }
                serialPort1.Close();
            }
            return serialPort1.IsOpen;
        }

        void wi_DataAvailable(object sender, WaveInEventArgs e) // 
        {
            int k = 4; // 1600 = 2^6 * 5^2. k is chunk size, not number of chunks (k*number_of_chunks = 1600)
            int s = 0;
            for (int i = 0; i < e.BytesRecorded; i += 2)
            {
                s += BitConverter.ToInt16(e.Buffer, i);
                if (i % k == 0)
                {
                    mic_Q.Enqueue(s / k);
                    mic_Q.Dequeue();
                    s = 0;
                }
                //mic_Q.Enqueue(BitConverter.ToInt16(e.Buffer, i));
                //mic_Q.Dequeue();
            }
        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            //mic constantly updates the at wi_DataAvailable(), independently from the timer)

            //sensors
            // gettin data from sensor1
            //WriteRead("$KE,IO,SET,1,0");

            string adc_raw_1; // example value is #ADC,0645
            int adc_value_1;

            string adc_raw_2; // example value is #ADC,0645
            int adc_value_2;



            // WARNING: test only one sensor at the same time

            //try //sensor damaged
            //{
            //    WriteRead("$KE,WR,1,0"); // set 0 to pin1. "$KE,WR,<LineNumber>,<Value>"
            //    adc_raw_1 = WriteRead("$KE,ADC");
            //    adc_value_1 = Convert.ToInt32("" + adc_raw_1[5] + adc_raw_1[6] + adc_raw_1[7] + adc_raw_1[8]);
            //    sensor1_Q.Enqueue(adc_value_1);
            //    sensor1_Q.Dequeue();
            //}
            //catch { Console.WriteLine("error at sensor1"); }



            //try //sensor working well 
            //{
            //    WriteRead("$KE,WR,1,1"); // set 1 to pin1
            //    adc_raw_2 = WriteRead("$KE,ADC");
            //    adc_value_2 = Convert.ToInt32("" + adc_raw_2[5] + adc_raw_2[6] + adc_raw_2[7] + adc_raw_2[8]);
            //    sensor2_Q.Enqueue(adc_value_2);
            //    sensor2_Q.Dequeue();
            //}
            //catch { Console.WriteLine("error at sensor2"); }

            draw_charts();
        }
    }
}

