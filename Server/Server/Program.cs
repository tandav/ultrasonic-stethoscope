using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Net.Sockets;
using System.Net;
using System.IO;
using System.IO.Compression;


namespace Socket_Test
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
                using (var client = listener.AcceptTcpClient())
                using (var stream = client.GetStream())
                using (var output = File.Create("signal.dat.gz"))
                {
                    Console.Write("Client connected. Starting to receive the file...");
                    var buffer = new byte[8192]; // blocksize = 8192 = 8KB
                    int bytesRead;
                    while ((bytesRead = stream.Read(buffer, 0, buffer.Length)) > 0)
                        output.Write(buffer, 0, bytesRead);
                }
                Console.WriteLine(" done\n");

                Console.Write("Decompression start...");
                byte[] file = File.ReadAllBytes("signal.dat.gz");
                byte[] decompressed = Decompress(file);
                float[] signal = new float[decompressed.Length / sizeof(float)];
                for (int i = 0; i < signal.Length; i++)
                    signal[i] = BitConverter.ToSingle(decompressed, sizeof(float) * i);
                Console.Write(" done\n");

                System.IO.DirectoryInfo di = new DirectoryInfo("fft"); //clean up fft folder for pics
                foreach (FileInfo pic in di.GetFiles())
                    pic.Delete();

                /////////////////////////////////// CUDA STUFF ////////////////////////////////////////
                Console.WriteLine("Start computing FFT with CUDA. Signal size = {0}...", signal.Length);
                // if you need to compute fft of whole signal:
                //float[] fft = new float[signal.Length / 2];
                
                int block_size = 32768*32; // signal is processing by blocks
                Console.WriteLine(block_size);
                float[] block = new float[block_size];
                float[] fft = new float[block_size / 2];

                int chart_points = 4000; // how many values draw on chart
                float[] block_to_draw = new float[chart_points]; // block of signal to draw on chart
                float[] fft_to_draw = new float[chart_points];


                for (int i = 0, file_count = 0; i < signal.Length; i += block_size, file_count++)
                {
                    if (i + block_size < signal.Length)
                        Array.Copy(signal, i, block, 0, block_size);
                    else // if "i" is close to end of signal - then copy all you can and fill rest w/ zeros
                    {
                        Array.Copy(signal, i, block, 0, signal.Length - i);
                        for (int j = signal.Length - i; j < block_size; j++)
                            block[j] = 0;
                    }

                    //CUDA.CUFT.Furie(block, fft, block_size);
                    //Fake FFT
                    for (int j = 0; j < block_size / 2; j++)
                        fft[j] = 0.01f * j * (block[2 * j] + block[2 * j + 1]) + 15000;

                    // optimize this big block
                    float signal_avg = block[0];
                    float fft_avg = fft[0];
                    int n = 1; 
                    int n2 = 1;

                    for (int j = 1, k = 0, t = 0; j < block_size; j++)
                    {
                        signal_avg += block[j];
                        n++;
                        if (j % (block_size / chart_points) == 0 || j + 1 == block_size)
                        {
                            block_to_draw[k] = signal_avg / n;
                            signal_avg = 0;
                            n = 0;
                            if (k + 1 < chart_points) k++;

                        }

                        if (j < block_size / 2)
                        {
                            fft_avg += fft[j];
                            n2++;
                            if (j % (block_size / 2 / chart_points) == 0 || j + 1 == block_size / 2)
                            {
                                fft_to_draw[t] = fft_avg / n2;
                                fft_avg = 0;
                                n2 = 0;
                                if (t + 1 < chart_points) t++;
                            }


                        }
                    }


                    Console.Write("Save to fft{0}.png start...", file_count);
                    save_pngs(block_to_draw, fft_to_draw, file_count);
                    Console.Write(" done\n");
                }
                Console.WriteLine("All PNGs are written");
                Console.WriteLine("==== Session end ====");
            }
        }

        static void save_pngs(float[] signal, float[] fft, int file_count)
        {
            System.Windows.Forms.DataVisualization.Charting.Chart chart = new System.Windows.Forms.DataVisualization.Charting.Chart();
            chart.Size = new System.Drawing.Size(1024, 512);
            chart.ChartAreas.Add("ChartArea1");
            chart.ChartAreas["ChartArea1"].BackColor = System.Drawing.Color.AliceBlue;
            chart.ChartAreas["ChartArea1"].AxisX.MajorGrid.LineColor = System.Drawing.Color.LightSteelBlue;
            chart.ChartAreas["ChartArea1"].AxisY.MajorGrid.LineColor = System.Drawing.Color.LightSteelBlue;
            chart.ChartAreas["ChartArea1"].AxisX.LineColor = System.Drawing.Color.DarkBlue;
            chart.ChartAreas["ChartArea1"].AxisY.LineColor = System.Drawing.Color.DarkBlue;
            chart.ChartAreas["ChartArea1"].AxisX.LabelStyle.Enabled = false;
            chart.ChartAreas["ChartArea1"].AxisY.LabelStyle.Enabled = false;
            chart.ChartAreas["ChartArea1"].AxisX.MajorTickMark.Enabled = false;
            chart.ChartAreas["ChartArea1"].AxisX.MinorTickMark.Enabled = false;
            chart.ChartAreas["ChartArea1"].AxisY.MajorTickMark.Enabled = false;
            chart.ChartAreas["ChartArea1"].AxisY.MinorTickMark.Enabled = false;
            //chart.ChartAreas["ChartArea1"].AxisX.LabelStyle.ForeColor = System.Drawing.Color.DarkBlue;
            //chart.ChartAreas["ChartArea1"].AxisY.LabelStyle.ForeColor = System.Drawing.Color.DarkBlue;
            chart.ChartAreas["ChartArea1"].Position.X = 0;
            chart.ChartAreas["ChartArea1"].Position.Width = 100;
            chart.ChartAreas["ChartArea1"].Position.Y = 0;
            chart.ChartAreas["ChartArea1"].Position.Height = 70;
            //chart.ChartAreas[0].AxisY.Minimum = 0; // temp for signal, not for fft
            //chart.ChartAreas[0].AxisY.Maximum = 3.5;
            chart.Series.Add("fft");
            chart.Series["fft"].Color = System.Drawing.Color.DarkBlue;
            chart.Series["fft"].ChartType = System.Windows.Forms.DataVisualization.Charting.SeriesChartType.Spline;
            chart.Series["fft"].Points.DataBindY(fft);

            chart.ChartAreas.Add("ChartArea2");
            chart.ChartAreas["ChartArea2"].BackColor = System.Drawing.Color.AliceBlue;
            chart.ChartAreas["ChartArea2"].AxisX.MajorGrid.LineColor = System.Drawing.Color.LightSteelBlue;
            chart.ChartAreas["ChartArea2"].AxisY.MajorGrid.LineColor = System.Drawing.Color.LightSteelBlue;
            chart.ChartAreas["ChartArea2"].AxisX.LineColor = System.Drawing.Color.DarkBlue;
            chart.ChartAreas["ChartArea2"].AxisY.LineColor = System.Drawing.Color.DarkBlue;
            chart.ChartAreas["ChartArea2"].AxisX.LabelStyle.Enabled = false;
            chart.ChartAreas["ChartArea2"].AxisY.LabelStyle.Enabled = false;
            chart.ChartAreas["ChartArea2"].AxisX.MajorTickMark.Enabled = false;
            chart.ChartAreas["ChartArea2"].AxisX.MinorTickMark.Enabled = false;
            chart.ChartAreas["ChartArea2"].AxisY.MajorTickMark.Enabled = false;
            chart.ChartAreas["ChartArea2"].AxisY.MinorTickMark.Enabled = false;
            //chart.ChartAreas["ChartArea2"].AxisX.LabelStyle.ForeColor = System.Drawing.Color.DarkBlue;
            //chart.ChartAreas["ChartArea2"].AxisY.LabelStyle.ForeColor = System.Drawing.Color.DarkBlue;
            chart.ChartAreas["ChartArea2"].Position.X = 0;
            chart.ChartAreas["ChartArea2"].Position.Width = 100;
            chart.ChartAreas["ChartArea2"].Position.Y = 72;
            chart.ChartAreas["ChartArea2"].Position.Height = 28;
            chart.ChartAreas[1].AxisY.Minimum = 0; // temp for signal, not for fft
            chart.ChartAreas[1].AxisY.Maximum = 3.5;
            chart.Series.Add("signal");
            chart.Series["signal"].Color = System.Drawing.Color.DarkBlue;
            chart.Series["signal"].ChartArea = "ChartArea2";
            chart.Series["signal"].ChartType = System.Windows.Forms.DataVisualization.Charting.SeriesChartType.Spline;
            chart.Series["signal"].Points.DataBindY(signal);

            chart.SaveImage("./fft/fft-" + file_count.ToString() + ".png", System.Drawing.Imaging.ImageFormat.Png);
        }

        static float[] SubArray(float[] data, int index, int length)
        {
            float[] result = new float[length];
            int data_len = data.Length;
            if (index + length < data_len)
                Array.Copy(data, index, result, 0, length);
            else // if we're close to end of data - then copy all you can and fill rest w/ zeros
            {
                Array.Copy(data, index, result, 0, data_len - index);
                for (int i = data_len - index; i < length; i++)
                    result[i] = 0;
            }
            return result;
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
            using (GZipStream stream = new GZipStream(new MemoryStream(gzip),
                CompressionMode.Decompress))
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