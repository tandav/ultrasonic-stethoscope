﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Net.Sockets;
using System.Net;
using System.IO;
using System.IO.Compression;

namespace Server
{
    class Program
    {
        static void Main(string[] args)
        {

            var listener = new TcpListener(IPAddress.Any, 5005);
            listener.Start();
            Console.WriteLine("This machine IP: {0} (maybe not really, check it out twice if troubles)", GetLocalIPAddress());
            while (true)
            {
                //using (var client = listener.AcceptTcpClient())
                //using (var stream = client.GetStream())
                //using (var output = File.Create("signal.dat.gz"))
                //{
                //    Console.Write("Client connected. Starting to receive the file...");
                //    var buffer = new byte[8192]; // blocksize = 8192 = 8KB
                //    int bytesRead;
                //    while ((bytesRead = stream.Read(buffer, 0, buffer.Length)) > 0)
                //        output.Write(buffer, 0, bytesRead);
                //}
                //Console.WriteLine(" done\n");

                Console.Write("Decompression start...");
                byte[] file = File.ReadAllBytes("signal.dat.gz");
                byte[] decompressed = Decompress(file);
                float[] signal = new float[decompressed.Length / sizeof(float) - 2]; // -2 'cause metadata
                for (int i = 0; i < signal.Length; i++)
                    signal[i] = BitConverter.ToSingle(decompressed, sizeof(float) * i);
                float record_time = BitConverter.ToSingle(decompressed, sizeof(float) * signal.Length);
                float rate = BitConverter.ToSingle(decompressed, sizeof(float) * (signal.Length + 1));
                Console.Write(" done\n");

                System.IO.DirectoryInfo di = new DirectoryInfo("fft"); //clean up fft folder for pics
                foreach (FileInfo pic in di.GetFiles())
                    pic.Delete();


                Console.WriteLine("Start computing FFT with CUDA");
                Console.WriteLine("Signal size = {0} \t record_time: {1} \t rate: {2}", signal.Length, record_time, rate);

                int signal_len = signal.Length;
                int block_size = (signal_len < 5000000) ? signal_len : 5000000; // you can try change 1048576 on real cuda server for better performance

                float[] block = new float[block_size];
                float[] time = new float[block_size];

                float[] fft = new float[block_size / 2];
                float[] freq = new float[block_size / 2]; // /2 => one side frequency range

                int chart_points = 5000; // how many values draw on chart
                float[] block_to_draw = new float[chart_points]; // block of signal to draw on chart
                float[] time_to_draw = new float[chart_points]; // block of signal to draw on chart

                float[] fft_to_draw = new float[chart_points];
                float[] freq_to_draw = new float[chart_points];


                for (int i = 0; i < signal_len; i += block_size)
                {
                    Array.Copy(signal, i, block, 0, block_size);

                    //CUDA.CUFT.Furie(block, fft, block_size); // normilised and (highly probably) abs(y)
                    //System.IO.File.WriteAllLines("fft.txt", fft.Select(tb => tb.ToString())); // save fft-shit to text file
                    //Fake FFT
                    for (int j = 0; j < block_size / 2; j++)
                        fft[j] = Math.Abs(-10f - (float)Math.Sin(0.01 * j) * (j - block_size / 2));

                    for (int j = 0; j < block_size / 2; j++) // Done?
                        freq[j] = (float)j / block_size * rate;

                    for (int j = 0; j < block_size; j++)
                        time[j] = record_time * ((float)i / block_size + (float)j / signal_len);

                    // optimize this big code block (with .NET's Sum, Take, Skip)
                    float signal_avg = block[0];
                    float time_avg = time[0];

                    float fft_avg = fft[0];
                    float freq_avg = freq[0];

                    int n = 1; 
                    int n2 = 1;
                    for (int j = 1, k = 0, t = 0; j < block_size; j++)
                    {
                        signal_avg += block[j];
                        time_avg   += time[j];
                        n++;
                        if (j % (block_size / chart_points) == 0 || j + 1 == block_size)
                        {
                            block_to_draw[k] = signal_avg / n; // n here is constant, you ain't need to recalculate it each iteration
                            time_to_draw[k]  = time_avg / n;
                            signal_avg       = 0;
                            time_avg         = 0;
                            n                = 0;
                            if (k + 1 < chart_points) k++;
                        }

                        if (j < block_size / 2)
                        {
                            fft_avg  += fft[j];
                            freq_avg += freq[j];
                            n2++;
                            if (j % ((block_size / 2) / chart_points) == 0 || j + 1 == (block_size / 2))
                            {
                                fft_to_draw[t]  = fft_avg / n2;
                                freq_to_draw[t] = freq_avg / n2;
                                fft_avg         = 0;
                                freq_avg        = 0;
                                n2              = 0;
                                if (t + 1 < chart_points) t++;
                            }
                        }
                    }

                    Console.Write("Save to fft{0}.png start...", i / block_size);
                    save_pngs(time_to_draw, block_to_draw, freq_to_draw, fft_to_draw, i / block_size);
                    Console.Write(" done\n");
                }
                Console.WriteLine("All PNGs are written");
                Console.WriteLine("==== Session end ====");
                //Console.ReadKey();
                break;
            }
        }

        static void save_pngs(float[] time, float[] signal, float[] freq, float[] fft, int file_count)
        {
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
            chart.ChartAreas["SignalArea"].AxisX.Minimum = 0;
            chart.ChartAreas["SignalArea"].AxisY.Minimum = 0;
            chart.ChartAreas["SignalArea"].AxisY.Maximum = 3.5;
            chart.Series.Add("signal");
            chart.Series["signal"].Color = System.Drawing.Color.DarkBlue;
            chart.Series["signal"].ChartArea = "SignalArea";
            chart.Series["signal"].ChartType = System.Windows.Forms.DataVisualization.Charting.SeriesChartType.Line;
            chart.Series["signal"].Points.DataBindXY(time, signal);


            chart.SaveImage("./fft/fft-" + file_count.ToString() + ".png", System.Drawing.Imaging.ImageFormat.Png);
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
