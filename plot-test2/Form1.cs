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

namespace plot_test2
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();

            // chart axis boundaries
            //chart1.ChartAreas[0].Axes[0].Minimum = -2;
            //chart1.ChartAreas[0].Axes[0].Maximum = 100;
            chart1.ChartAreas[0].Axes[1].Minimum = -2;
            chart1.ChartAreas[0].Axes[1].Maximum = 2;
        }
        //double t = 0;
        int n = 200; // number of x-axis pints
        //double x = 5; 
        //double[] data = new double[60];
        Stopwatch time = new Stopwatch();
        

        double get_value(double x) // in future mb array of values(chunk from mic data)
        {
            return Math.Sin(x);
        }

        private void update_data()
        {
            //data[data.Length - 1] = time.ElapsedMilliseconds;
            //Array.Copy(data, 1, data, 0, data.Length - 1);

            //chart1.Series["Series1"].Points.Clear();
            double curr_t = time.ElapsedMilliseconds;
            //chart1.Series["Series1"].Points.AddXY(x/n*i, Math.Sin(5 / n * i + t));
            chart1.Series["Series1"].Points.RemoveAt(0);
            chart1.Series["Series1"].Points.AddXY(curr_t, Math.Sin(curr_t));
            chart1.ChartAreas[0].Axes[0].Minimum = chart1.Series["Series1"].Points.First().XValue;
            chart1.ChartAreas[0].Axes[0].Maximum = chart1.Series["Series1"].Points.Last().XValue;

            Console.WriteLine(chart1.Series["Series1"].Points.First().XValue);

            //chart1.ChartAreas[0].Axes[0].Minimum = chart1.Series["Series1"].Points.Min();
            //chart1.ChartAreas[0].Axes[0].Maximum = chart1.Series["Series1"].Points.FindMaxByValue("X", 0).XValue;

            //chart1.ResetAutoValues();
            //chart1.Update();
            //chart1.Refresh();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            
            for (int i = 0; i < n; i++)
                chart1.Series["Series1"].Points.AddXY(0.0, 0.0);

            time.Start();
            timer1.Enabled = true;

        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            update_data();
            //t += 0.1;
        }
    }
}