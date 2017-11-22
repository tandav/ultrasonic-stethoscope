using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace bin_to_array
{
    class Program
    {
        static void Main(string[] args)
        {
            using (var filestream = File.Open(@"data.dat", FileMode.Open))
            using (var binaryStream = new BinaryReader(filestream))
            {
                while (binaryStream.BaseStream.Position != binaryStream.BaseStream.Length)
                {
                    Console.WriteLine(binaryStream.ReadSingle());
                }
                Console.ReadKey();
            }
        }
    }
}
