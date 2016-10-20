using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace plot_test2
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
            
            // chart axis boundaries
            chart1.ChartAreas[0].Axes[0].Minimum = -2;
            chart1.ChartAreas[0].Axes[0].Maximum = 2;
            chart1.ChartAreas[0].Axes[1].Minimum = -2;
            chart1.ChartAreas[0].Axes[1].Maximum = 2;
        }
        double t = 0;

        private void update_data()
        {
            chart1.Series["Series1"].Points.Clear();
            for (int i = 0; i < 4; i++)
            {
                chart1.Series["Series1"].Points.AddXY(i, Math.Sin(i + t));
            }
        }

        private void button1_Click(object sender, EventArgs e)
        {


            timer1.Enabled = true;
            
        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            update_data();
            t += 0.1;
        }
    }
}
