using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Sockets;
using System.Net;
using System.Text;
using System.Threading.Tasks;
using System.Threading;

namespace Test
{
    class Program
    {

        /// <summary>
        /// Считывает данные по сети
        /// </summary>
        /// <param name="ns">Соединение по сети</param>
        /// <param name="Size">Размер считываемых данных</param>
        /// <returns></returns>
        private static byte[] Read(NetworkStream ns, int Size)
        {
            byte[] buf = new byte[Size];
            int N = ns.Read(buf, 0, Size);
            int S = 0;
            while (N != Size)
            {
                S += N;
                Size -= N;
                N = ns.Read(buf, S, Size);
            }
            return buf;
        }

        static void Main(string[] args)
        {
            TcpListener Listener = new TcpListener(IPAddress.Any, int.Parse(args[1].Trim()));
            Listener.Start();

            while (true)
            {
                if (Listener.Pending())
                {
                    TcpClient Client = Listener.AcceptTcpClient();
                    NetworkStream ns = Client.GetStream();

                    int N = BitConverter.ToInt32(Read(ns, 4), 0);

                    float[] data = new float[N];
                    float[] furie = new float[N / 2 + 1];

                    for (int I = 0; I < N; I++)
                        data[I] = BitConverter.ToSingle(Read(ns, sizeof(float)), 0);

                    for (int I = 0; I < data.Length; I++)
                        data[I] = (float)Math.Sin(Math.PI * I / 3);

                    CUDA.CUFT.Furie(data, furie, 1000);

                    byte[] buf = new byte[4 + furie.Length * sizeof(float)];

                    Array.Copy(BitConverter.GetBytes(furie.Length), 0, buf, 0, 4);
                    for (int I = 0; I < furie.Length; I++)
                        Array.Copy(BitConverter.GetBytes(furie[I]), 0, buf, 4 + I * sizeof(float), sizeof(float));
                    ns.Write(buf, 0, buf.Length);

                    Client.Close();
                }
                else
                    Thread.Sleep(100);
            }
        }
    }
}
