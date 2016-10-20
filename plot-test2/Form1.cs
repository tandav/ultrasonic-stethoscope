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
        }
        double r = 0.1;
        private void button1_Click(object sender, EventArgs e)
        {
            chart1.Series["Series1"].Points.Clear();
            for (int i = 0; i < 500; i++)
            {
                chart1.Series["Series1"].Points.AddXY(i, r*Math.Sin(i));
                r += 0.1;
            }
        }
    }
}
