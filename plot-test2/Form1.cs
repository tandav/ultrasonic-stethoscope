using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Diagnostics;
using NAudio.Wave;
using NAudio;

namespace plot_test2
{
    public partial class Form1 : Form
    {
        int n = 2000; // number of x-axis pints
        //Stopwatch time = new Stopwatch();
        WaveIn wi;
        
        public Form1()

        {
            InitializeComponent();
            // chart axis boundaries
            //chart1.ChartAreas[0].Axes[0].Minimum = -32768;
            //chart1.ChartAreas[0].Axes[0].Maximum = 32767;
            chart1.ChartAreas[0].Axes[1].Minimum = -32768/2;
            chart1.ChartAreas[0].Axes[1].Maximum = 32767/2;
            //chart1.ChartAreas[0].Axes[1].Minimum = 150000;
            //chart1.ChartAreas[0].Axes[1].Maximum = 250000;
        }


        private void button1_Click(object sender, EventArgs e)
        {
            for (int i = 0; i < n; i++)
                chart1.Series["Series1"].Points.AddXY(0.0, 0.0);
            wi = new WaveIn();
            wi.StartRecording();
            //wi.WaveFormat = new WaveFormat(44100, 16, 1); //tipa navern nado, try delete
            wi.WaveFormat = new WaveFormat(16, 16, 1); //tipa navern nado, try delete

            wi.DataAvailable += new EventHandler<WaveInEventArgs>(wi_DataAvailable);
        }


        void wi_DataAvailable(object sender, WaveInEventArgs e)
        {
            //Console.WriteLine(sample);

            short sample;
            // old way. dont need data[] array, but not showing plot properly in the begining seconds
            for (int i = 0; i < e.BytesRecorded;i += 2)
            {
                //  Console.WriteLine(sample);
                sample = BitConverter.ToInt16(e.Buffer, i);

                chart1.Series["Series1"].Points.RemoveAt(0);
                chart1.Series["Series1"].Points.AddY(sample);
                chart1.ResetAutoValues();

                //chart1.Series["Series1"].Points.RemoveAt(0);
                //chart1.Series["Series1"].Points.AddXY(time.ElapsedMilliseconds, sample);
                //chart1.ChartAreas[0].Axes[0].Minimum = chart1.Series["Series1"].Points.First().XValue;
                //chart1.ChartAreas[0].Axes[0].Maximum = chart1.Series["Series1"].Points.Last().XValue;
                //chart1.ResetAutoValues();
            }


            //chart1.ChartAreas[0].Axes[0].Minimum = chart1.Series["Series1"].Points.First().XValue;
            //chart1.ChartAreas[0].Axes[0].Maximum = chart1.Series["Series1"].Points.Last().XValue;

            //time.Start();
        }
        private void update_data()
        {

        }
        private void timer1_Tick(object sender, EventArgs e)
        {
            //update_data();
        }
    }
}