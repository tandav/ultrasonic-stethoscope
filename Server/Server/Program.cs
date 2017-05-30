using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Net.Sockets;
using System.Net;
using System.IO;
using System.IO.Compression;
using System.Threading;

namespace Server
{
    class Program
    {
        static void Main(string[] args)
        {
            while (true)
            {
                receive_and_write_to_file();

                Console.Write("decompressing signal.dat.gz...");
                byte[] file = File.ReadAllBytes("signal.dat.gz");
                byte[] decompressed = Decompress(file);
                float[] signal = new float[decompressed.Length / sizeof(float) - 2]; // -2 'cause metadata [record_time, rate] at the end of file
                for (int i = 0; i < signal.Length; i++)
                    signal[i] = BitConverter.ToSingle(decompressed, sizeof(float) * i);
                float record_time = BitConverter.ToSingle(decompressed, sizeof(float) * signal.Length);
                float rate = BitConverter.ToSingle(decompressed, sizeof(float) * (signal.Length + 1));
                Console.Write(" done\n");

                receive_fft();
                Console.Write("decompressing fft.dat.gz...");
                byte[] fft_b = File.ReadAllBytes("fft.dat.gz");
                byte[] fft_b_d = Decompress(fft_b);
                int fft_dat_len = fft_b_d.Length / sizeof(float);
                float[] freq_received = new float[fft_dat_len / 2]; // 1st half of file
                float[] fft_received  = new float[fft_dat_len / 2]; // 2nd half of file
                for (int i = 0; i < fft_dat_len / 2; i++)
                {
                    freq_received[i] = BitConverter.ToSingle(fft_b_d, sizeof(float) * i);
                    fft_received [i] = BitConverter.ToSingle(fft_b_d, sizeof(float) * (i + fft_dat_len / 2));
                }
                Console.Write(" done\n");

                System.IO.DirectoryInfo di = new DirectoryInfo("fft"); //clean up fft folder for pics
                foreach (FileInfo pic in di.GetFiles())
                    pic.Delete();

                Console.WriteLine("Signal size = {0} \t record_time: {1} \t rate: {2}", signal.Length, record_time, rate);
                Console.Write("Start computing FFT with CUDA...");

                int signal_len = signal.Length;
                int block_size = (signal_len < 5000000) ? signal_len : 5000000;

                float[] block = new float[block_size];
                float[] time  = new float[block_size];
                float[] freq  = new float[block_size / 2]; 
                float[] fft   = new float[block_size / 2];
                
                int chart_points      = 5000; // (block_size / 2) % chart_points == 0 (SHOULD BE)
                float[] block_to_draw = new float[chart_points];
                float[] time_to_draw  = new float[chart_points];
                float[] freq_to_draw  = new float[chart_points];
                float[] fft_to_draw   = new float[chart_points];
                int avg_points_signal = block_size / chart_points; // points to avg
                int avg_points_fft = block_size / chart_points / 2;

                for (int i = 0; i < signal_len; i += block_size)
                {
                    Array.Copy(signal, i, block, 0, block_size);

                    //CUDA.CUFT.Furie(block, fft, block_size); // normilised and (highly probably) abs(y)
                    //Fake FFT
                    for (int j = 0; j < block_size / 2; j++)
                    {
                        freq[j] = freq_received[j];
                        fft [j] = fft_received [j];
                        //fft[j] = Math.Abs(-10f - (float)Math.Sin(0.01 * j) * (j - block_size / 2));
                    }

                    for (int j = 0; j < block_size / 2; j++)
                        freq[j] = (float)j / block_size * rate;

                    for (int j = 0; j < block_size; j++)
                        time[j] = record_time * ((float)i / block_size + (float)j / signal_len);

                    for (int j = 0; j < chart_points; j++) // averaging arrays to plot less values 
                    {
                        block_to_draw[j] = block.Skip(j * avg_points_signal).Take(avg_points_signal).Sum() / avg_points_signal;
                        time_to_draw [j] = time .Skip(j * avg_points_signal).Take(avg_points_signal).Sum() / avg_points_signal;
                        fft_to_draw  [j] = fft  .Skip(j * avg_points_fft)   .Take(avg_points_fft)   .Sum() / avg_points_fft;
                        freq_to_draw [j] = freq .Skip(j * avg_points_fft)   .Take(avg_points_fft)   .Sum() / avg_points_fft;
                    }
                    save_pngs(time_to_draw, block_to_draw, freq_to_draw, fft_to_draw, i / block_size);
                }
                Console.WriteLine("all PNGs are written");
                Console.WriteLine("session end================================\n\n");
                //break;
            }
        }

        static void receive_and_write_to_file()
        {
            var listener = new TcpListener(IPAddress.Any, 5005);
            listener.Start();
            Console.WriteLine("This machine IP: {0} (maybe not really, check it out twice if troubles)", GetLocalIPAddress());

            using (var client = listener.AcceptTcpClient())
            using (var stream = client.GetStream())
            using (var output = File.Create("signal.dat.gz"))
            {
                Console.Write("client connected. receiving the signal...");
                var buffer = new byte[8192]; // blocksize = 8192 = 8KB
                int bytesRead;
                while ((bytesRead = stream.Read(buffer, 0, buffer.Length)) > 0)
                    output.Write(buffer, 0, bytesRead);
            }
            Console.WriteLine(" done");
            listener.Stop();
        }

        static void receive_fft(bool receive_fft = false)
        {
            var listener_fft = new TcpListener(IPAddress.Any, 5005);
            listener_fft.Start();
            using (var client = listener_fft.AcceptTcpClient())
            using (var stream = client.GetStream())
            using (var output = File.Create("fft.dat.gz"))
            {
                Console.Write("receiving fft...");
                var buffer = new byte[8192]; // blocksize = 8192 = 8KB
                int bytesRead;
                while ((bytesRead = stream.Read(buffer, 0, buffer.Length)) > 0)
                    output.Write(buffer, 0, bytesRead);
            }
            Console.WriteLine(" done");
            listener_fft.Stop();
        }

        static void save_pngs(float[] time, float[] signal, float[] freq, float[] fft, int file_count)
        {
            Console.Write("Save to fft{0}.png start...", file_count);

            System.Windows.Forms.DataVisualization.Charting.Chart chart = new System.Windows.Forms.DataVisualization.Charting.Chart();
            chart.Size = new System.Drawing.Size(1400, 700);
            System.Drawing.Color darkblue = System.Drawing.Color.DarkBlue;

            chart.ChartAreas.Add("FFT_Area");
            chart.ChartAreas["FFT_Area"].Position.X = 0;
            chart.ChartAreas["FFT_Area"].Position.Width = 95;
            chart.ChartAreas["FFT_Area"].Position.Y = 0;
            chart.ChartAreas["FFT_Area"].Position.Height = 70;
            chart.ChartAreas["FFT_Area"].BackColor = System.Drawing.Color.AliceBlue;
            chart.ChartAreas["FFT_Area"].AxisX.MajorGrid.LineColor = System.Drawing.Color.LightSteelBlue;
            chart.ChartAreas["FFT_Area"].AxisY.MajorGrid.LineColor = System.Drawing.Color.LightSteelBlue;
            chart.ChartAreas["FFT_Area"].AxisX.LineColor = darkblue;
            chart.ChartAreas["FFT_Area"].AxisY.LineColor = darkblue;
            chart.ChartAreas["FFT_Area"].AxisX.LabelStyle.ForeColor = darkblue;
            chart.ChartAreas["FFT_Area"].AxisY.LabelStyle.ForeColor = darkblue;
            chart.ChartAreas["FFT_Area"].AxisY.MajorTickMark.LineColor = darkblue;
            chart.ChartAreas["FFT_Area"].AxisX.MinorGrid.Interval = 1;
            chart.ChartAreas["FFT_Area"].AxisX.MinorGrid.Enabled = true;
            chart.ChartAreas["FFT_Area"].AxisX.MinorGrid.LineColor = System.Drawing.Color.FromArgb(223, 231, 241);
            chart.ChartAreas["FFT_Area"].AxisX.MajorTickMark.Enabled = true;
            chart.ChartAreas["FFT_Area"].AxisX.MinorTickMark.Enabled = true;
            chart.ChartAreas["FFT_Area"].AxisX.MajorTickMark.Size = 1.5f;
            chart.ChartAreas["FFT_Area"].AxisX.MinorTickMark.Size = 0.5f;
            chart.ChartAreas["FFT_Area"].AxisX.MajorTickMark.Interval = 1;
            chart.ChartAreas["FFT_Area"].AxisX.MinorTickMark.Interval = 1;
            chart.ChartAreas["FFT_Area"].AxisX.MajorTickMark.LineColor = darkblue;
            chart.ChartAreas["FFT_Area"].AxisX.MinorTickMark.LineColor = darkblue;
            chart.ChartAreas["FFT_Area"].AxisX.Title = "Frequency, Hz";
            chart.ChartAreas["FFT_Area"].AxisX.TitleForeColor = darkblue;
            chart.ChartAreas["FFT_Area"].AxisY.Title = "Amplitude, dB";
            chart.ChartAreas["FFT_Area"].AxisY.TitleForeColor = darkblue;
            chart.ChartAreas["FFT_Area"].BorderWidth = 1;
            chart.ChartAreas["FFT_Area"].BorderDashStyle = System.Windows.Forms.DataVisualization.Charting.ChartDashStyle.Solid;
            chart.ChartAreas["FFT_Area"].BorderColor = darkblue;
            chart.ChartAreas["FFT_Area"].AxisX.IsLogarithmic = true;
            chart.ChartAreas["FFT_Area"].AxisY.IsLogarithmic = true;
            chart.ChartAreas["FFT_Area"].AxisX.LabelStyle.Format = "#.e+0";
            chart.ChartAreas["FFT_Area"].AxisY.LabelStyle.Format = "#.e+0";
            chart.ChartAreas["FFT_Area"].AxisX.Minimum = 10; // IMPORTANT this is influence on LogScale success and errors must be > 0 
            //chart.ChartAreas["FFT_Area"].AxisY.Minimum = 0; // temp for signal, not for fft
            //chart.ChartAreas["FFT_Area"].AxisY.Maximum = 0.000001;

            chart.Series.Add("fft");
            chart.Series["fft"].Color = System.Drawing.Color.DarkBlue;
            chart.Series["fft"].ChartType = System.Windows.Forms.DataVisualization.Charting.SeriesChartType.Line;
            chart.Series["fft"].Points.DataBindXY(freq, fft);


            chart.ChartAreas.Add("SignalArea");
            chart.ChartAreas["SignalArea"].Position.Y = 72;
            chart.ChartAreas["SignalArea"].Position.Height = 28;
            chart.ChartAreas["SignalArea"].AlignWithChartArea = "FFT_Area";
            chart.ChartAreas["SignalArea"].BackColor = System.Drawing.Color.AliceBlue;
            chart.ChartAreas["SignalArea"].AxisX.MajorGrid.LineColor = System.Drawing.Color.LightSteelBlue;
            chart.ChartAreas["SignalArea"].AxisY.MajorGrid.LineColor = System.Drawing.Color.LightSteelBlue;
            chart.ChartAreas["SignalArea"].AxisX.LineColor = darkblue;
            chart.ChartAreas["SignalArea"].AxisY.LineColor = darkblue;
            chart.ChartAreas["SignalArea"].AxisX.LabelStyle.ForeColor = darkblue;
            chart.ChartAreas["SignalArea"].AxisY.LabelStyle.ForeColor = darkblue;
            chart.ChartAreas["SignalArea"].AxisX.MajorTickMark.LineColor = darkblue;
            chart.ChartAreas["SignalArea"].AxisY.MajorTickMark.LineColor = darkblue;
            chart.ChartAreas["SignalArea"].AxisX.MinorGrid.Interval = 0.1;
            chart.ChartAreas["SignalArea"].AxisX.MinorGrid.Enabled = true;
            chart.ChartAreas["SignalArea"].AxisX.MinorGrid.LineColor = System.Drawing.Color.FromArgb(223, 231, 241);
            chart.ChartAreas["SignalArea"].AxisX.Title = "Time, seconds";
            chart.ChartAreas["SignalArea"].AxisX.TitleForeColor = darkblue;
            chart.ChartAreas["SignalArea"].AxisY.Title = "Voltage, V";
            chart.ChartAreas["SignalArea"].AxisY.TitleForeColor = darkblue;
            chart.ChartAreas["SignalArea"].BorderWidth = 1;
            chart.ChartAreas["SignalArea"].BorderDashStyle = System.Windows.Forms.DataVisualization.Charting.ChartDashStyle.Solid;
            chart.ChartAreas["SignalArea"].BorderColor = darkblue;
            chart.ChartAreas["SignalArea"].AxisX.MajorTickMark.Interval = 0.5;
            chart.ChartAreas["SignalArea"].AxisX.MajorTickMark.Size = 1.5f;
            chart.ChartAreas["SignalArea"].AxisX.MinorTickMark.Enabled = true;
            chart.ChartAreas["SignalArea"].AxisX.MinorTickMark.Size = 0.5f;
            chart.ChartAreas["SignalArea"].AxisX.MinorTickMark.Interval = 0.1;
            chart.ChartAreas["SignalArea"].AxisX.MinorTickMark.LineColor = darkblue;
            chart.ChartAreas["SignalArea"].AxisX.LabelStyle.Format = "0.##";
            chart.ChartAreas["SignalArea"].AxisY.LabelStyle.Format = "0.##";
            chart.ChartAreas["SignalArea"].AxisX.Minimum = 0;
            chart.ChartAreas["SignalArea"].AxisY.Minimum = signal.Min();
            chart.ChartAreas["SignalArea"].AxisY.Maximum = signal.Max();
            //chart.ChartAreas["SignalArea"].AxisY.Minimum = 0;
            //chart.ChartAreas["SignalArea"].AxisY.Maximum = 3.5;
            chart.Series.Add("signal");
            chart.Series["signal"].Color = System.Drawing.Color.DarkBlue;
            chart.Series["signal"].ChartArea = "SignalArea";
            chart.Series["signal"].ChartType = System.Windows.Forms.DataVisualization.Charting.SeriesChartType.Line;
            chart.Series["signal"].Points.DataBindXY(time, signal);

            Console.Write("...");
            chart.SaveImage("./fft/fft-" + file_count.ToString() + ".png", System.Drawing.Imaging.ImageFormat.Png);
            Console.Write(" done\n");

        }

        static string GetLocalIPAddress()
        {
            var host = Dns.GetHostEntry(Dns.GetHostName());
            foreach (var ip in host.AddressList)
            {
                if (ip.AddressFamily == AddressFamily.InterNetwork)
                {
                    return ip.ToString();
                }
            }
            throw new Exception("Local IP Address Not Found!");
        }

        static byte[] Decompress(byte[] gzip)
        {
            // Create a GZIP stream with decompression mode.
            // ... Then create a buffer and write into while reading from the GZIP stream.
            using (GZipStream stream = new GZipStream(new MemoryStream(gzip), CompressionMode.Decompress))
            {
                const int size = 4096;
                byte[] buffer = new byte[size];
                using (MemoryStream memory = new MemoryStream())
                {
                    int count = 0;
                    do
                    {
                        count = stream.Read(buffer, 0, size);
                        if (count > 0)
                        {
                            memory.Write(buffer, 0, count);
                        }
                    }
                    while (count > 0);
                    return memory.ToArray();
                }
            }
        }
    }
}
