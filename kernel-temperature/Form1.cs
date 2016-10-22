using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.IO.Ports;

namespace kernel_temperature
{
    public partial class Form1 : Form
    {
        SerialPort serialPort1;
        int n = 500; // number of x-axis pints
        //Stopwatch time = new Stopwatch();
        Queue<double> adc1_Q;
        Queue<double> adc2_Q;

        public Form1()
        {
            InitializeComponent();
            adc1_Q = new Queue<double>(Enumerable.Repeat(0.0, n).ToList()); // fill myQ w/ zeros
            serialPort1 = new SerialPort();
            serialPort1.ReadTimeout = 50;
            serialPort1.WriteTimeout = 50;
            //chart1.ChartAreas[0].Axes[1].Minimum = -10000;
            //chart1.ChartAreas[0].Axes[1].Maximum = 10000;
        }

        void draw_charts()
        {
            chart1.Series["Series1"].Points.DataBindY(adc1_Q);
        }

        void Form1_Load(object sender, EventArgs e)
        {
            if (SearchKeUSB()) timer1.Enabled = true;
            else label1.Text = "Error: Can't connect to Kernel Chip";
        }

        string WriteRead(string requiry)
        {
            serialPort1.Write(requiry);
            string message;
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
                    if (WriteRead("$KE\r\n").Substring(0, 3) == "#OK") break;
                }
                catch { }
                serialPort1.Close();
            }
            return serialPort1.IsOpen;
        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            // gettin data from sensor1
            WriteRead("$KE,IO,SET,1,0\r\n");
            WriteRead("$KE,WR,1,1\r\n");
            string re = WriteRead("$KE,ADC\r\n");
            try
            {
                int adc1_value = Convert.ToInt32("" + re[5] + re[6] + re[7] + re[8]);
                adc1_Q.Enqueue(adc1_value);
                adc1_Q.Dequeue();
            }
            catch
            {
                Console.WriteLine("Fuckin error at int adc1_value = Convert.ToInt32, ADC Value is: " + re);
            }

            draw_charts();
        }
    }
}
