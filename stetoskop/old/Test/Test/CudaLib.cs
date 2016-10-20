using System;
using System.Runtime.InteropServices;

namespace CUDA
{
    /// <summary>
    /// Класс, в котором реализованы все функции библиотеки CUFT.dll
    /// </summary>
    public static class CUFT
    {
        /// <summary>
        /// Возвращает текст ошибки по коду
        /// </summary>
        /// <param name="errorCode">код ошибки</param>
        /// <returns>текст ошибки</returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern string cuftGetErrorString(int errorCode);

        /// <summary>
        /// Вызывает ошибку, если код ошибки отличен от нуля
        /// </summary>
        /// <param name="errorCode">Код ошибки</param>
        private static void checkError(int errorCode)
        {
            if (errorCode != 0)
                throw new Exception(cuftGetErrorString(errorCode));
        }

        /// <summary>
        /// Возвращает процентное соотношение загруженности памяти видеокарты
        /// </summary>
        /// <param name="Volume">Процент загруженности памяти видеокарты</param>
        /// <returns>код ошибки</returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern int cuftGetMemGPU(out int Volume);

        /// <summary>
        /// Возвращает процентное соотношение загруженности памяти видеокарты
        /// </summary>
        /// <returns>Процент загруженности памяти видеокарты</returns>
        public static int GetMemGPU()
        {
            int n;
            checkError(cuftGetMemGPU(out n));
            return n;
        }

        /// <summary>
        /// Взвращает длину вейвлета
        /// </summary>
        /// <param name="N">Максимальный масштаб</param>
        /// <param name="kind">Тип вейвлета</param>
        /// <returns>Длина вейвлета</returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern int cuftWavletLength(int N, int kind);

        /// <summary>
        /// Взвращает длину вейвлета
        /// </summary>
        /// <param name="N">Максимальный масштаб</param>
        /// <param name="kind">Тип вейвлета</param>
        /// <returns>Длина вейвлета</returns>
        public static int WavletLength(int N, int kind)
        {
            return cuftWavletLength(N, kind);
        }
    
        /// <summary>
        /// Возвращает количество максимумов по заданным трем диапазонам, соответствующим R, G и B каналам 
        /// </summary>
        /// <param name="R1">Первый канал для красного</param>
        /// <param name="R2">Второй канал для красного</param>
        /// <param name="G1">Первый канал для зеленого</param>
        /// <param name="G2">Второй канал для зеленого</param>
        /// <param name="B1">Первый канал для синего</param>
        /// <param name="B2">Второй канал для синего</param>
        /// <param name="N">Число элементов в массивах</param>
        /// <param name="R">Полученный красный</param>
        /// <param name="G">Полученный зеленый</param>
        /// <param name="B">Полученный синий</param>
        /// <returns>Код ошибки или 0 в случае успешной работы</returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern int cuftColorQualifierCovExec([MarshalAs(UnmanagedType.LPArray)] float[] R1, 
            [MarshalAs(UnmanagedType.LPArray)] float[] R2, [MarshalAs(UnmanagedType.LPArray)] float[] G1, 
            [MarshalAs(UnmanagedType.LPArray)] float[] G2, [MarshalAs(UnmanagedType.LPArray)] float[] B1, 
            [MarshalAs(UnmanagedType.LPArray)] float[] B2, int N, ref float R, ref float G, ref float B);

        /// <summary>
        /// Возвращает количество максимумов по заданным трем диапазонам, соответствующим R, G и B каналам 
        /// </summary>
        /// <param name="R1">Первый канал для красного</param>
        /// <param name="R2">Второй канал для красного</param>
        /// <param name="G1">Первый канал для зеленого</param>
        /// <param name="G2">Второй канал для зеленого</param>
        /// <param name="B1">Первый канал для синего</param>
        /// <param name="B2">Второй канал для синего</param>
        /// <param name="N">Число элементов в массивах</param>
        /// <param name="R">Полученный красный</param>
        /// <param name="G">Полученный зеленый</param>
        /// <param name="B">Полученный синий</param>
        public static void ColorQualifierCov(float[] R1, float[] R2, float[] G1, float[] G2, float[] B1, float[] B2, 
            int N, ref float R, ref float G, ref float B)
        {
            checkError(cuftColorQualifierCovExec(R1, R2, G1, G2, B1, B2, N, ref R, ref G, ref B));
        }

        /// <summary>
        /// Расчет преобразования Фурье
        /// </summary>
        /// <param name="data">массив данных</param>
        /// <param name="Furie">массив результатов (N / 2 + 1)</param>
        /// <param name="N">число элементов в массиве data</param>
        /// <param name="Normal">применить нормировку</param>
        /// <returns>Код ошибки</returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern int cuftFurieExec([MarshalAs(UnmanagedType.LPArray)] float[] data, [MarshalAs(UnmanagedType.LPArray)] float[] Furie, int N, bool Normal);

        /// <summary>
        /// Расчет преобразования Фурье
        /// </summary>
        /// <param name="data">массив данных</param>
        /// <param name="Furie">массив результатов (N / 2 + 1)</param>
        /// <param name="N">число элементов в массиве data</param>
        /// <param name="Normal">применить нормировку</param>
        public static void Furie(float[] data, float[] Furie, int N, bool Normal = true)
        {
            checkError(cuftFurieExec(data, Furie, N, Normal));
        }

        /// <summary>
        /// Расчет вейвлета
        /// </summary>
        /// <param name="data">массив данных</param>
        /// <param name="Wavlet">Двумерный массив результатов (NxM)</param>
        /// <param name="N">Число элементов в массиве Data</param>
        /// <param name="M">Максимальный масштаб</param>
        /// <param name="fromM">Минимальный масштаб</param>
        /// <param name="kind">Тип вейвлета</param>
        /// <returns>Код ошибки</returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern int cuftWavletExec([MarshalAs(UnmanagedType.LPArray)] float[] data, [MarshalAs(UnmanagedType.LPArray)] float[] Wavlet, int N, ref int M, int fromM, int kind);

        /// <summary>
        /// Расчет вейвлета
        /// </summary>
        /// <param name="data">массив данных</param>
        /// <param name="Wavlet">Двумерный массив результатов (NxM)</param>
        /// <param name="N">Число элементов в массиве Data</param>
        /// <param name="M">Максимальный масштаб</param>
        /// <param name="fromM">Минимальный масштаб</param>
        /// <param name="kind">Тип вейвлета</param>
        public static void Wavlet(float[] data, float[] Wavlet, int N, ref int M, int fromM, int kind)
        {
            checkError(cuftWavletExec(data, Wavlet, N, ref M, fromM, kind));
        }

        /// <summary>
        /// Расчет вейвлета без смещения
        /// </summary>
        /// <param name="data">массив данных</param>
        /// <param name="Wavlet">Двумерный массив результатов (NxM)</param>
        /// <param name="N">Число элементов в массиве Data</param>
        /// <param name="M">Максимальный масштаб</param>
        /// <param name="fromM">Минимальный масштаб</param>
        /// <param name="kind">Тип вейвлета</param>
        /// <returns>Код ошибки</returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern int cuftWavlet0Exec([MarshalAs(UnmanagedType.LPArray)] float[] data, [MarshalAs(UnmanagedType.LPArray)] float[] Wavlet, int N, int M, int fromM, int kind);

        /// <summary>
        /// Расчет вейвлета без смещения
        /// </summary>
        /// <param name="data">массив данных</param>
        /// <param name="Wavlet">Двумерный массив результатов (NxM)</param>
        /// <param name="N">Число элементов в массиве Data</param>
        /// <param name="M">Максимальный масштаб</param>
        /// <param name="fromM">Минимальный масштаб</param>
        /// <param name="kind">Тип вейвлета</param>
        public static void Wavlet0(float[] data, float[] Wavlet, int N, int M, int fromM, int kind)
        {
            checkError(cuftWavlet0Exec(data, Wavlet, N, M, fromM, kind));
        }

        /// <summary>
        /// Вычисляется размах вевлета
        /// </summary>
        /// <param name="data">Начальные данные</param>
        /// <param name="Wavlet">Вейвлет коэффициенты возведенные в квадрат</param>
        /// <param name="sweep">Размах отсортированный</param>
        /// <param name="N">Число элементов</param>
        /// <param name="M">Максимальный масштаб</param>
        /// <param name="fromM">Минимальный масштаб</param>
        /// <param name="kind">Тип вейвлета</param>
        /// <param name="point">Точка относительно которой вычисляется размах</param>
        /// <returns>Код ошибки или 0, если функция выполнена успешно</returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern int cuftWavletSweepExec([MarshalAs(UnmanagedType.LPArray)] float[] data,
            [MarshalAs(UnmanagedType.LPArray)] float[] Wavlet, [MarshalAs(UnmanagedType.LPArray)] int[] sweep,
            int N, int M, int fromM, int kind, int point);

        /// <summary>
        /// Вычисляется размах вевлета
        /// </summary>
        /// <param name="data">Начальные данные</param>
        /// <param name="Wavlet">Вейвлет коэффициенты возведенные в квадрат</param>
        /// <param name="sweep">Размах отсортированный</param>
        /// <param name="N">Число элементов</param>
        /// <param name="M">Максимальный масштаб</param>
        /// <param name="fromM">Минимальный масштаб</param>
        /// <param name="kind">Тип вейвлета</param>
        /// <param name="point">Точка относительно которой вычисляется размах</param>
        public static void cuftWavletSweep(float[] data, float[] Wavlet, int[] sweep, int N, 
            int M, int fromM, int kind, int point)
        {
            checkError(cuftWavletSweepExec(data, Wavlet, sweep, N, M, fromM, kind, point));
        }

        /// <summary>
        /// /приводит сигнал к нормальной форме удалив среднее и не побразный тренд
        /// </summary>
        /// <param name="data">массив данных сигнала</param>
        /// <param name="N">Длина сигнала</param>
        /// <param name="M">Число каналов</param>
        /// <returns>Код ошибки или 0, если функция выполнена успешно</returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern int cuftNormSignalExec([MarshalAs(UnmanagedType.LPArray)] float[] data, int N, int M);

        /// <summary>
        /// /приводит сигнал к нормальной форме удалив среднее и не побразный тренд
        /// </summary>
        /// <param name="data">массив данных сигнала</param>
        /// <param name="N">Длина сигнала</param>
        /// <param name="M">Число каналов</param>
        public static void cuftNormSignal(float[] data, int N, int M)
        {
            checkError(cuftNormSignalExec(data, N, M));
        }

        /// <summary>
        /// Выполняет свертку
        /// </summary>
        /// <param name="f">Массив данных сворачиваемой функции</param>
        /// <param name="N">Число элементов в массиве f</param>
        /// <param name="g">Массив данных функции по которой идет свертка</param>
        /// <param name="M">Число элементов в массиве g</param>
        /// <param name="c">Массив с результатом свертки</param>
        /// <returns>Код ошибки или 0, если функция выполнена успешно</returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern int cuftGetConvolution([MarshalAs(UnmanagedType.LPArray)] float[] f, int N,
            [MarshalAs(UnmanagedType.LPArray)] float[] g, int M, [MarshalAs(UnmanagedType.LPArray)] float[] c);

        /// <summary>
        /// Выполняет свертку
        /// </summary>
        /// <param name="f">Массив данных сворачиваемой функции</param>
        /// <param name="N">Число элементов в массиве f</param>
        /// <param name="g">Массив данных функции по которой идет свертка</param>
        /// <param name="M">Число элементов в массиве g</param>
        /// <param name="c">Массив с результатом свертки</param>
        public static void cuftConvolution(float[] f, int N, float[] g, int M, float[] c)
        {
            checkError(cuftGetConvolution(f, N, g, M, c));
        }

        /// <summary>
        /// Суммирует данные в каналах
        /// </summary>
        /// <param name="data">Исходные данные в каналах</param>
        /// <param name="N">Число элементов в канале</param>
        /// <param name="M">Число каналов</param>
        /// <param name="result">Результат суммы</param>
        /// <returns>Код ошибки или 0, если функция выполнена успешно</returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern int cuftSumExec([MarshalAs(UnmanagedType.LPArray)] float[] data, int N, int M,
            [MarshalAs(UnmanagedType.LPArray)] float[] result);

        /// <summary>
        /// Суммирует данные в каналах
        /// </summary>
        /// <param name="data">Исходные данные в каналах</param>
        /// <param name="N">Число элементов в канале</param>
        /// <param name="M">Число каналов</param>
        /// <param name="result">Результат суммы</param>
        public static void cuftSum(float[] data, int N, int M, float[] result)
        {
            checkError(cuftSumExec(data, N, M, result));
        }

        /// <summary>
        /// Вычисляет карту минимумов и максимумов
        /// </summary>
        /// <param name="data">Исходные данные (вейвлет)</param>
        /// <param name="map">Результат (массив коэффициентов)</param>
        /// <param name="N">Число отсчетов</param>
        /// <param name="M">Масштаб</param>
        /// <returns>Код ошибки или 0</returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern int cuftMapExtremumExec([MarshalAs(UnmanagedType.LPArray)] float[] data,
            [MarshalAs(UnmanagedType.LPArray)] int[] map, int N, int M);

        /// <summary>
        /// Вычисляет карту минимумов и максимумов
        /// </summary>
        /// <param name="data">Исходные данные (вейвлет)</param>
        /// <param name="map">Результат (массив коэффициентов)</param>
        /// <param name="N">Число отсчетов</param>
        /// <param name="M">Масштаб</param>
        public static void cuftMapExtremum(float[] data, int[] map, int N, int M)
        {
            checkError(cuftMapExtremumExec(data, map, N, M));
        }
    }
}