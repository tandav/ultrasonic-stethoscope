using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Test
{
    class Program
    {
        static void Main(string[] args)
        {
            float[] data = new float[1000000];
            float[] furie = new float[data.Length / 2 + 1];

            for (int I = 0; I < data.Length; I++)
                data[I] = (float)Math.Sin(Math.PI * I / 3);

            CUDA.CUFT.Furie(data, furie, 1000);

            for (int I = 0; I < furie.Length; I++)
            {
                Console.Write(furie[I]);
                Console.Write(" ");
            }

            Console.ReadKey();
        }
    }
}
