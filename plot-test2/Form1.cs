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

namespace plot_test2
{
    public partial class Form1 : Form
    {
        int n = 200; // number of x-axis pints
        Stopwatch time = new Stopwatch();
        WaveIn wi;
        byte x;
        public Form1()
        {
            InitializeComponent();

            // chart axis boundaries
            //chart1.ChartAreas[0].Axes[0].Minimum = -2;
            //chart1.ChartAreas[0].Axes[0].Maximum = 100;
            //chart1.ChartAreas[0].Axes[1].Minimum = -2;
            //chart1.ChartAreas[0].Axes[1].Maximum = 2;
        }


        double get_value(double x) // in future mb array of values(chunk from mic data)
        {
            return Math.Sin(x);
        }

        private void update_data()
        {

            //chart1.Series["Series1"].Points.Clear();
            double curr_t = time.ElapsedMilliseconds;

            // old way. dont need data[] array, but not showing plot properly in the begining seconds
            chart1.Series["Series1"].Points.RemoveAt(0);
            chart1.Series["Series1"].Points.AddXY(curr_t, x);
            chart1.ChartAreas[0].Axes[0].Minimum = chart1.Series["Series1"].Points.First().XValue;
            chart1.ChartAreas[0].Axes[0].Maximum = chart1.Series["Series1"].Points.Last().XValue;

            Console.WriteLine(chart1.Series["Series1"].Points.First().XValue);


            chart1.ResetAutoValues();
            //chart1.Update();
            //chart1.Refresh();
        }

        private void button1_Click(object sender, EventArgs e)
        {


            for (int i = 0; i < n; i++)
                chart1.Series["Series1"].Points.AddXY(0.0, 0.0);
            wi = new WaveIn();
            wi.StartRecording();
            wi.WaveFormat = new WaveFormat(44100, 1); //tipa navern nado, try delete
            wi.DataAvailable += new EventHandler<WaveInEventArgs>(wi_DataAvailable);
            //wi.RecordingStopped += new EventHandler<StoppedEventArgs>(wi_RecordingStopped);





        }

        void wi_DataAvailable(object sender, WaveInEventArgs e)
        {
            
            for (int I = 0; I < e.BytesRecorded; I++)
            {
                x = (byte)Math.Abs(e.Buffer[I] - 127);
            }

            time.Start();
            timer1.Enabled = true;
        }

        //void waveSource_RecordingStopped(object sender, StoppedEventArgs e)
        //{
        //    if (waveSource != null)
        //    {
        //        waveSource.Dispose();
        //        waveSource = null;
        //    }

        //    if (waveFile != null)
        //    {
        //        waveFile.Dispose();
        //        waveFile = null;
        //    }

        //    StartBtn.Enabled = true;
        //}

        private void timer1_Tick(object sender, EventArgs e)
        {
            update_data();
        }
    }
}