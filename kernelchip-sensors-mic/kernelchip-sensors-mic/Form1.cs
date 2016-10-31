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
        int n_mic = 400; //number of x-axis points
        //Stopwatch time = new Stopwatch();
        WaveIn wi;
        Queue<double> mic_Q;

        //sensors
        SerialPort serialPort1;
        int n_sensors = 400; // number of x-axis points
        //Stopwatch time = new Stopwatch();
        Queue<double> sensor1_Q;
        Queue<double> sensor2_Q;

        public Form1()
        {
            InitializeComponent();
        }


        private void Form1_Load(object sender, EventArgs e)
        {
            //mic
            mic_Q = new Queue<double>(Enumerable.Repeat(0.0, n_mic).ToList()); // fill mic_Q w/ zeros
            chart1.ChartAreas[0].AxisY.Minimum = -1200;
            chart1.ChartAreas[0].AxisY.Maximum = 1200;
            wi = new WaveIn();
            wi.StartRecording();
            wi.WaveFormat = new WaveFormat(44100, 16, 1);
            wi.DataAvailable += new EventHandler<WaveInEventArgs>(wi_DataAvailable);
            timer1.Enabled = true;
            //time.Start();

            //sensors
            sensor1_Q = new Queue<double>(Enumerable.Repeat(0.0, n_sensors).ToList()); // fill w/ zeros
            sensor2_Q = new Queue<double>(Enumerable.Repeat(0.0, n_sensors).ToList()); // fill w/ zeros
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

        //void wi_DataAvailable(object sender, WaveInEventArgs e) // 
        //{
        //    double s = 0;
        //    for (int i = 0; i < e.BytesRecorded; i += 2)
        //    {
        //        s += BitConverter.ToInt16(e.Buffer, i);
        //        //mic_Q.Enqueue(BitConverter.ToInt16(e.Buffer, i));
        //        //mic_Q.Dequeue();
        //    }

        //    mic_Q.Enqueue(s / e.BytesRecorded / 2);
        //    mic_Q.Dequeue();
        //}


        void wi_DataAvailable(object sender, WaveInEventArgs e) // 
        {
            int k = 64;
            double s = 0;
            for (int i = 0; i < e.BytesRecorded; i += 2)
            {
                s += BitConverter.ToInt16(e.Buffer, i);
                if (i % k == 0)
                {
                    mic_Q.Enqueue(s / k / 2);
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
            string adc_raw; // example value is #ADC,0645
            //try
            //{
            //    WriteRead("$KE,WR,1,0"); // set 0 to pin1
            //    adc_raw = WriteRead("$KE,ADC");
            //    int sensor1_value = Convert.ToInt32("" + adc_raw[5] + adc_raw[6] + adc_raw[7] + adc_raw[8]);
            //    sensor1_Q.Enqueue(sensor1_value);
            //    sensor1_Q.Dequeue();
            //}
            //catch { Console.WriteLine("error at sensor1"); }
            //catch { Console.WriteLine("error at sensor1 = Convert.ToInt32, ADC Value is: " + adc_raw); }



            try
            {
                WriteRead("$KE,WR,1,1"); // set 1 to pin1
                adc_raw = WriteRead("$KE,ADC");
                int sensor2_value = Convert.ToInt32("" + adc_raw[5] + adc_raw[6] + adc_raw[7] + adc_raw[8]);
                sensor2_Q.Enqueue(sensor2_value);
                sensor2_Q.Dequeue();
            }
            catch { Console.WriteLine("error at sensor2"); }

            draw_charts();
        }
    }
}

