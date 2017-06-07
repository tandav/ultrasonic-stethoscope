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
     //   [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
     //   private static extern string cuftGetErrorString(int errorCode);

        /// <summary>
        /// Вызывает ошибку, если код ошибки отличен от нуля
        /// </summary>
        /// <param name="errorCode">Код ошибки</param>
        private static void checkError(int errorCode)
        {
            if (errorCode != 0)
                throw new Exception("Ошибка куды: " + errorCode.ToString());
        }

        /// <summary>
        /// Возвращает процентное соотношение загруженности памяти видеокарты
        /// </summary>
        /// <param name="volume">Процент загруженности памяти видеокарты</param>
        /// <returns>код ошибки</returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern int cuftGetMemGPU(out int volume);

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
        /// <param name="n">Максимальный масштаб</param>
        /// <param name="kind">Тип вейвлета</param>
        /// <returns>Длина вейвлета</returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern int cuftWavletLength(int n, int kind);

        /// <summary>
        /// Взвращает длину вейвлета
        /// </summary>
        /// <param name="n">Максимальный масштаб</param>
        /// <param name="kind">Тип вейвлета</param>
        /// <returns>Длина вейвлета</returns>
        public static int WavletLength(int n, int kind)
        {
            return cuftWavletLength(n, kind);
        }
    
        /// <summary>
        /// Возвращает количество максимумов по заданным трем диапазонам, соответствующим R, G и B каналам 
        /// </summary>
        /// <param name="r1">Первый канал для красного</param>
        /// <param name="r2">Второй канал для красного</param>
        /// <param name="g1">Первый канал для зеленого</param>
        /// <param name="g2">Второй канал для зеленого</param>
        /// <param name="b1">Первый канал для синего</param>
        /// <param name="b2">Второй канал для синего</param>
        /// <param name="n">Число элементов в массивах</param>
        /// <param name="r">Полученный красный</param>
        /// <param name="g">Полученный зеленый</param>
        /// <param name="b">Полученный синий</param>
        /// <returns>Код ошибки или 0 в случае успешной работы</returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern int cuftColorQualifierCovExec([MarshalAs(UnmanagedType.LPArray)] float[] r1, 
            [MarshalAs(UnmanagedType.LPArray)] float[] r2, [MarshalAs(UnmanagedType.LPArray)] float[] g1, 
            [MarshalAs(UnmanagedType.LPArray)] float[] g2, [MarshalAs(UnmanagedType.LPArray)] float[] b1, 
            [MarshalAs(UnmanagedType.LPArray)] float[] b2, int n, out float r, out float g, out float b);

        /// <summary>
        /// Возвращает количество максимумов по заданным трем диапазонам, соответствующим R, G и B каналам 
        /// </summary>
        /// <param name="r1">Первый канал для красного</param>
        /// <param name="r2">Второй канал для красного</param>
        /// <param name="g1">Первый канал для зеленого</param>
        /// <param name="g2">Второй канал для зеленого</param>
        /// <param name="b1">Первый канал для синего</param>
        /// <param name="b2">Второй канал для синего</param>
        /// <param name="n">Число элементов в массивах</param>
        /// <param name="r">Полученный красный</param>
        /// <param name="g">Полученный зеленый</param>
        /// <param name="b">Полученный синий</param>
        public static void ColorQualifierCov(float[] r1, float[] r2, float[] g1, float[] g2, float[] b1, float[] b2, 
            int n, out float r, out float g, out float b)
        {
            checkError(cuftColorQualifierCovExec(r1, r2, g1, g2, b1, b2, n, out r, out g, out b));
        }

        /// <summary>
        /// Вычисляется корреляция между двумя массивами a и b
        /// </summary>
        /// <param name="a">Первый массив</param>
        /// <param name="b">Второй массив</param>
        /// <param name="n">Число элементов</param>
        /// <param name="cov">Результаты корреляции</param>
        /// <returns>Код ошибки или 0</returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern int cuftCovExec([MarshalAs(UnmanagedType.LPArray)] float[] a, [MarshalAs(UnmanagedType.LPArray)] float[] b, int n, out float cov);

        /// <summary>
        /// Вычисляется корреляция между двумя массивами a и b
        /// </summary>
        /// <param name="a">Первый массив</param>
        /// <param name="b">Второй массив</param>
        /// <param name="n">Число элементов</param>
        /// <returns>Результаты корреляции</returns>
        public static float Cov(float[] a, float[] b, int n)
        {
            float cov;
            checkError(cuftCovExec(a, b, n, out cov));
            return cov;
        }

        /// <summary>
        /// вычисляется корреляция между опорным и другими сигналами
        /// </summary>
        /// <param name="a">Матрица сигналов. Первый столбец - опорный сигнал</param>
        /// <param name="n">Длина сигналов</param>
        /// <param name="m">Число сигналов, которые нужно скоррелировать с опорным</param>
        /// <param name="cov">Результат корреляции</param>
        /// <returns></returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern int cuftCovSignalsExec([MarshalAs(UnmanagedType.LPArray)] float[] a, int n, int m, [MarshalAs(UnmanagedType.LPArray)] float[] cov);

        /// <summary>
        /// вычисляется корреляция между опорным и другими сигналами
        /// </summary>
        /// <param name="a">Матрица сигналов. Первый столбец - опорный сигнал</param>
        /// <param name="n">Длина сигналов</param>
        /// <param name="m">Число сигналов, которые нужно скоррелировать с опорным</param>
        /// <param name="cov">Результат корреляции</param>
        public static void CovSignals(float[] a, int n, int m, float[] cov)
        {
            checkError(cuftCovSignalsExec(a, n, m, cov));
        }

        /// <summary>
        /// Расчет преобразования Фурье
        /// </summary>
        /// <param name="data">массив данных</param>
        /// <param name="furie">массив результатов (N / 2 + 1)</param>
        /// <param name="n">число элементов в массиве data</param>
        /// <param name="normal">применить нормировку</param>
        /// <returns>Код ошибки</returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern int cuftFurieExec([MarshalAs(UnmanagedType.LPArray)] float[] data, [MarshalAs(UnmanagedType.LPArray)] float[] furie, int n, bool normal);

        /// <summary>
        /// Расчет преобразования Фурье
        /// </summary>
        /// <param name="data">массив данных</param>
        /// <param name="furie">массив результатов (N / 2 + 1)</param>
        /// <param name="n">число элементов в массиве data</param>
        /// <param name="normal">применить нормировку</param>
        public static void Furie(float[] data, float[] furie, int n, bool normal = true)
        {
            checkError(cuftFurieExec(data, furie, n, normal));
        }

        /// <summary>
        /// Расчет вейвлета
        /// </summary>
        /// <param name="data">массив данных</param>
        /// <param name="wavlet">Двумерный массив результатов (NxM)</param>
        /// <param name="n">Число элементов в массиве Data</param>
        /// <param name="m">Максимальный масштаб</param>
        /// <param name="fromM">Минимальный масштаб</param>
        /// <param name="kind">Тип вейвлета</param>
        /// <returns>Код ошибки</returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern int cuftWavletExec([MarshalAs(UnmanagedType.LPArray)] float[] data, [MarshalAs(UnmanagedType.LPArray)] float[] wavlet, int n, ref int m, int fromM, int kind);

        /// <summary>
        /// Расчет вейвлета
        /// </summary>
        /// <param name="data">массив данных</param>
        /// <param name="wavlet">Двумерный массив результатов (NxM)</param>
        /// <param name="n">Число элементов в массиве Data</param>
        /// <param name="m">Максимальный масштаб</param>
        /// <param name="fromM">Минимальный масштаб</param>
        /// <param name="kind">Тип вейвлета</param>
        public static void Wavlet(float[] data, float[] wavlet, int n, ref int m, int fromM, int kind)
        {
            checkError(cuftWavletExec(data, wavlet, n, ref m, fromM, kind));
        }

        /// <summary>
        /// Расчет вейвлета без смещения
        /// </summary>
        /// <param name="data">массив данных</param>
        /// <param name="wavlet">Двумерный массив результатов (NxM)</param>
        /// <param name="n">Число элементов в массиве Data</param>
        /// <param name="m">Максимальный масштаб</param>
        /// <param name="fromM">Минимальный масштаб</param>
        /// <param name="kind">Тип вейвлета</param>
        /// <returns>Код ошибки</returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern int cuftWavlet0Exec([MarshalAs(UnmanagedType.LPArray)] float[] data, [MarshalAs(UnmanagedType.LPArray)] float[] wavlet, int n, int m, int fromM, int kind);

        /// <summary>
        /// Расчет вейвлета без смещения
        /// </summary>
        /// <param name="data">массив данных</param>
        /// <param name="wavlet">Двумерный массив результатов (NxM)</param>
        /// <param name="n">Число элементов в массиве Data</param>
        /// <param name="m">Максимальный масштаб</param>
        /// <param name="fromM">Минимальный масштаб</param>
        /// <param name="kind">Тип вейвлета</param>
        public static void Wavlet0(float[] data, float[] wavlet, int n, int m, int fromM, int kind)
        {
            checkError(cuftWavlet0Exec(data, wavlet, n, m, fromM, kind));
        }

        /// <summary>
        /// Вычисляется размах вевлета
        /// </summary>
        /// <param name="data">Начальные данные</param>
        /// <param name="Wavlet">Вейвлет коэффициенты возведенные в квадрат</param>
        /// <param name="sweep">Размах отсортированный</param>
        /// <param name="n">Число элементов</param>
        /// <param name="m">Максимальный масштаб</param>
        /// <param name="fromM">Минимальный масштаб</param>
        /// <param name="kind">Тип вейвлета</param>
        /// <param name="point">Точка относительно которой вычисляется размах</param>
        /// <returns>Код ошибки или 0, если функция выполнена успешно</returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern int cuftWavletSweepExec([MarshalAs(UnmanagedType.LPArray)] float[] data,
            [MarshalAs(UnmanagedType.LPArray)] float[] Wavlet, [MarshalAs(UnmanagedType.LPArray)] int[] sweep,
            int n, int m, int fromM, int kind, int point);

        /// <summary>
        /// Вычисляется размах вевлета
        /// </summary>
        /// <param name="data">Начальные данные</param>
        /// <param name="wavlet">Вейвлет коэффициенты возведенные в квадрат</param>
        /// <param name="sweep">Размах отсортированный</param>
        /// <param name="n">Число элементов</param>
        /// <param name="m">Максимальный масштаб</param>
        /// <param name="fromM">Минимальный масштаб</param>
        /// <param name="kind">Тип вейвлета</param>
        /// <param name="point">Точка относительно которой вычисляется размах</param>
        public static void cuftWavletSweep(float[] data, float[] wavlet, int[] sweep, int n, 
            int m, int fromM, int kind, int point)
        {
            checkError(cuftWavletSweepExec(data, wavlet, sweep, n, m, fromM, kind, point));
        }

        /// <summary>
        /// /приводит сигнал к нормальной форме удалив среднее и не побразный тренд
        /// </summary>
        /// <param name="data">массив данных сигнала</param>
        /// <param name="n">Длина сигнала</param>
        /// <param name="m">Число каналов</param>
        /// <returns>Код ошибки или 0, если функция выполнена успешно</returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern int cuftNormSignalExec([MarshalAs(UnmanagedType.LPArray)] float[] data, int n, int m);

        /// <summary>
        /// /приводит сигнал к нормальной форме удалив среднее и не побразный тренд
        /// </summary>
        /// <param name="data">массив данных сигнала</param>
        /// <param name="n">Длина сигнала</param>
        /// <param name="m">Число каналов</param>
        public static void cuftNormSignal(float[] data, int n, int m)
        {
            checkError(cuftNormSignalExec(data, n, m));
        }

        /// <summary>
        /// Выполняет свертку
        /// </summary>
        /// <param name="f">Массив данных сворачиваемой функции</param>
        /// <param name="n">Число элементов в массиве f</param>
        /// <param name="g">Массив данных функции по которой идет свертка</param>
        /// <param name="m">Число элементов в массиве g</param>
        /// <param name="c">Массив с результатом свертки</param>
        /// <returns>Код ошибки или 0, если функция выполнена успешно</returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern int cuftGetConvolution([MarshalAs(UnmanagedType.LPArray)] float[] f, int n,
            [MarshalAs(UnmanagedType.LPArray)] float[] g, int m, [MarshalAs(UnmanagedType.LPArray)] float[] c);

        /// <summary>
        /// Выполняет свертку
        /// </summary>
        /// <param name="f">Массив данных сворачиваемой функции</param>
        /// <param name="n">Число элементов в массиве f</param>
        /// <param name="g">Массив данных функции по которой идет свертка</param>
        /// <param name="m">Число элементов в массиве g</param>
        /// <param name="c">Массив с результатом свертки</param>
        public static void cuftConvolution(float[] f, int n, float[] g, int m, float[] c)
        {
            checkError(cuftGetConvolution(f, n, g, m, c));
        }

        /// <summary>
        /// Суммирует данные в каналах
        /// </summary>
        /// <param name="data">Исходные данные в каналах</param>
        /// <param name="n">Число элементов в канале</param>
        /// <param name="m">Число каналов</param>
        /// <param name="result">Результат суммы</param>
        /// <returns>Код ошибки или 0, если функция выполнена успешно</returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern int cuftSumExec([MarshalAs(UnmanagedType.LPArray)] float[] data, int n, int m,
            [MarshalAs(UnmanagedType.LPArray)] float[] result);

        /// <summary>
        /// Суммирует данные в каналах
        /// </summary>
        /// <param name="data">Исходные данные в каналах</param>
        /// <param name="n">Число элементов в канале</param>
        /// <param name="m">Число каналов</param>
        /// <param name="result">Результат суммы</param>
        public static void cuftSum(float[] data, int n, int m, float[] result)
        {
            checkError(cuftSumExec(data, n, m, result));
        }

        /// <summary>
        /// Вычисляет карту минимумов и максимумов
        /// </summary>
        /// <param name="data">Исходные данные (вейвлет)</param>
        /// <param name="map">Результат (массив коэффициентов)</param>
        /// <param name="n">Число отсчетов</param>
        /// <param name="m">Масштаб</param>
        /// <returns>Код ошибки или 0</returns>
        [DllImport("CUFT.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern int cuftMapExtremumExec([MarshalAs(UnmanagedType.LPArray)] float[] data,
            [MarshalAs(UnmanagedType.LPArray)] int[] map, int n, int m);

        /// <summary>
        /// Вычисляет карту минимумов и максимумов
        /// </summary>
        /// <param name="data">Исходные данные (вейвлет)</param>
        /// <param name="map">Результат (массив коэффициентов)</param>
        /// <param name="n">Число отсчетов</param>
        /// <param name="m">Масштаб</param>
        public static void cuftMapExtremum(float[] data, int[] map, int n, int m)
        {
            checkError(cuftMapExtremumExec(data, map, n, m));
        }
    }
}