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
            Console.WriteLine("This machine IP: {0}", GetLocalIPAddress());
            while (true)
            {
                using (var client = listener.AcceptTcpClient())
                using (var stream = client.GetStream())
                using (var output = File.Create("data.dat.gz"))
                {
                    Console.WriteLine("Client connected. Starting to receive the file...");

                    // read the file in chunks of 1KB
                    // var buffer = new byte[1024];

                    var buffer = new byte[8192]; // blocksize = 8192 = 8KB
            
                    int bytesRead;
                    while ((bytesRead = stream.Read(buffer, 0, buffer.Length)) > 0)
                    {
                        output.Write(buffer, 0, bytesRead);
                    }
                }
                Console.WriteLine("Received the file");
                Console.WriteLine("Decompression start...");

                // Decompress .gz
                byte[] file = File.ReadAllBytes("data.dat.gz");
                byte[] decompressed = Decompress(file);
                double[] data = new double[decompressed.Length / sizeof(double)];

                for (int i = 0; i < data.Length; i++)
                {
                    data[i] = BitConverter.ToDouble(decompressed, sizeof(double) * i);
                    //Console.WriteLine(data[i]);
                }
                float[] signal = Array.ConvertAll(data, x => (float)x); // convert to float array to use CUDA library
                Console.WriteLine("Decompression success...");

                //for (int i = 0; i < signal.Length; i++)
                //    Console.WriteLine(signal[i]);

                Console.WriteLine("FFT start. Signal size = {0}...", signal.Length);

                // CUDA FFT
                //float[] fft = new float[signal.Length / 2]; // write to disk very slow, reduced fft.len by 1000
                float[] fft = new float[signal.Length / 500];

                //CUDA.CUFT.Furie(signal, fft, signal.Length); // здесь почему то в моем коде . Вахтина был третий аргумент 1000, возможно ошибка но если траблы будут - поставить 1000 или у вахтина спросить

                // temp transofrm, just for test, TODO: del
                for (int i = 0; i < fft.Length; i++)
                {
                    //fft[i] = signal[2 * i]; // not fft for test!!!!
                    //fft[i] = signal[500 * i]; // not fft for test!!!!
                    fft[i] = signal[i]; // not fft for test!!!!


                }
                Console.WriteLine("FFT success");

                Console.WriteLine("Save to PNG start...");
                System.Windows.Forms.DataVisualization.Charting.Chart chart = new System.Windows.Forms.DataVisualization.Charting.Chart();
                chart.Size = new System.Drawing.Size(640, 320);
                chart.ChartAreas.Add("ChartArea1");
                chart.ChartAreas[0].AxisY.Minimum = 0; // temp for signal, not for fft
                chart.ChartAreas[0].AxisY.Maximum = 4;

                chart.Series.Add("fft");
                chart.Series["fft"].ChartType = System.Windows.Forms.DataVisualization.Charting.SeriesChartType.Spline;
                chart.Series["fft"].Points.DataBindY(fft);
                chart.SaveImage("fft.png", System.Drawing.Imaging.ImageFormat.Png);
                Console.WriteLine("Save to PNG success");

            }
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
