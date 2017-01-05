#include <stdio.h>
#include <stdarg.h>
// #include <conio.h>
#include <math.h>
#include <windows.h>
// #include <winioctl.h>
#include "Lusbapi.h"

/*================================================================================================*/
#define DAC_FREQ        200000
#define DAC_BUF_SAMPLES 100000
#define ADC_FREQ        100000
#define ADC_BUF_SAMPLES 50000

#define CH_GAIN_1       0x00 /* 10 V */
#define CH_GAIN_4       0x40 /* 2.5 V */
#define CH_GAIN_16      0x80 /* 0.625 V */
#define CH_GAIN_64      0xC0 /* 0.15625 V */
#define CH_MODE_DIFF    0x00
#define CH_MODE_CGROUND 0x20
#define CH_MEASURE_ZERO 0x10 /* only when CH_MODE_CGROUND == 0 */

#define CTL_TOGGLE      1
#define CTL_TERMINATE   2
#define CTL_SLEEP       3

#define TID_DAC         0
#define TID_ADC         1

/* Отладочные параметры */
#define MARK_DAC_START  1
#define ZERO_ON_STOP    0
#define FLIP_FLOP_AMP   0
/*================================================================================================*/

/*================================================================================================*/
ILE140 *pModule;
HANDLE ModuleHandle;
CRITICAL_SECTION cs;
ADC_PARS_E140 ap;
DAC_PARS_E140 dp;
short int DAC_Buf[DAC_BUF_SAMPLES][2];    /* Один буфер на 2 канала */
short int ADC_Buf[2][ADC_BUF_SAMPLES][2]; /* Два буфера на 2 канала */
BYTE bConst_1 = 1;

/* Переменные для связи с потоками */
const char *pThreadMessage[2] = { NULL, NULL };
HANDLE hControlEvent[2];
HANDLE hThreadMsgEvent[2];
int Control[2] = { 0, 0 };
/*================================================================================================*/

/*------------------------------------------------------------------------------------------------*/
static void f_CloseHandles(int Count, HANDLE *pList)
    {
    while (Count--)
        {
        if (*pList != INVALID_HANDLE_VALUE)
            {
            CloseHandle(*pList);
            *pList = INVALID_HANDLE_VALUE;
            }
        pList++;
        }
    }
/*------------------------------------------------------------------------------------------------*/

/*------------------------------------------------------------------------------------------------*/
static void f_ThreadMsg(int TID, const char *msg)
    {
    if (TID < 2)
        {
        pThreadMessage[TID] = msg;
        SetEvent(hThreadMsgEvent[TID]);
        }
    }
/*------------------------------------------------------------------------------------------------*/

/*------------------------------------------------------------------------------------------------*/
static void f_PrintThreadMsg(int TID, const char *prefix)
    {
    if (TID > 1) return;
    if (pThreadMessage[TID])
        {
        printf("%s: %s\n", prefix, pThreadMessage[TID]);
        pThreadMessage[TID] = NULL;
        }
    }
/*------------------------------------------------------------------------------------------------*/

/*------------------------------------------------------------------------------------------------*/
DWORD WINAPI ControlThread(LPVOID)
    {
    for (;;)
        {
        switch (getch())
            {
            case 'a':
            case 'A':
                Control[TID_ADC] = CTL_TOGGLE;
                SetEvent(hControlEvent[TID_ADC]);
                break;
            case 's':
            case 'S':
                Control[TID_ADC] = CTL_SLEEP;
                SetEvent(hControlEvent[TID_ADC]);
                break;
            case 'd':
            case 'D':
                Control[TID_DAC] = CTL_TOGGLE;
                SetEvent(hControlEvent[TID_DAC]);
                break;
            case 0x1B:
                Control[TID_DAC] = CTL_TERMINATE;
                SetEvent(hControlEvent[TID_DAC]);
                Control[TID_ADC] = CTL_TERMINATE;
                SetEvent(hControlEvent[TID_ADC]);
                return 0; /* Подав команду выхода, завершаемся сами */
            }
        }
    return 0;
    }
/*------------------------------------------------------------------------------------------------*/

/*------------------------------------------------------------------------------------------------*/
DWORD WINAPI ADC_Thread(LPVOID)
    {
    const int TID = TID_ADC;
    int running = 0;
    int idx = 0;
    HANDLE hEvent[2] = {INVALID_HANDLE_VALUE, INVALID_HANDLE_VALUE };
    OVERLAPPED ov[2];
    unsigned int StartCount = 1;
    static char FileName[64];
    HANDLE hFile = INVALID_HANDLE_VALUE;
    DWORD dummy, TransferSize;
    int ok;

    for (;;)
        {
        if (!running)
            {
            WaitForSingleObject(hControlEvent[TID], INFINITE);
            switch (Control[TID])
                {
                case CTL_TERMINATE:      /* Завершение программы */
                    return 0; /* Ничего не открыто, так что просто выйти */
                case CTL_SLEEP:
                    EnterCriticalSection(&cs);
                    if (pModule->PutArray(&bConst_1, 1, 0x430))
                        {
                        f_ThreadMsg(TID, "Sleep mode engaged");
                        }
                    else
                        {
                        f_ThreadMsg(TID, "Cannot enter sleep mode");
                        }
                    LeaveCriticalSection(&cs);
                    break;
                case CTL_TOGGLE:        /* Запуск АЦП */
                    hEvent[0] = CreateEvent(NULL, TRUE, FALSE, NULL);
                    hEvent[1] = CreateEvent(NULL, TRUE, FALSE, NULL);
                    ok = 0;
                    EnterCriticalSection(&cs);
                    do
                        {
                        if (!pModule->SET_ADC_PARS(&ap))
                            {
                            f_ThreadMsg(TID, "Cannot set ADC parameters");
                            break;
                            }
                        /* Формируем имя файла */
                        sprintf(FileName, "adc%03u.dat", StartCount);
                        /* Открываем файл */
                        hFile = CreateFile(FileName, GENERIC_WRITE, FILE_SHARE_READ, NULL,
                            CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL | FILE_FLAG_SEQUENTIAL_SCAN |
                            FILE_FLAG_WRITE_THROUGH, NULL);
                        if (hFile == INVALID_HANDLE_VALUE)
                            {
                            f_ThreadMsg(TID, "Cannot create data file");
                            break;
                            }
                        /* Ставим в очередь первый запрос чтения данных */
                        ZeroMemory(&ov[0], sizeof(OVERLAPPED));
                        ov[0].hEvent = hEvent[0];
                        if (!ReadFile(ModuleHandle, ADC_Buf[0], sizeof(ADC_Buf[0]), NULL, &ov[0])
                            && (GetLastError() != ERROR_IO_PENDING))
                            {
                            f_ThreadMsg(TID, "ReadFile() failed during start");
                            CloseHandle(hFile);
                            break;
                            }
                        /* Запускаем АЦП */
                        if (!pModule->START_ADC())
                            {
                            f_ThreadMsg(TID, "Cannot start ADC");
                            CloseHandle(hFile);
                            break;
                            }
                        idx = 1;
                        running = 1;
                        f_ThreadMsg(TID, "ADC started");
                        StartCount++;
                        ok = 1;
                        }
                    while (0);
                    LeaveCriticalSection(&cs);
                    if (!ok)
                        f_CloseHandles(2, hEvent);
                    break;
                }
            }
        else /* running */
            {
            /* Ставим в очередь следующий буфер */
            ZeroMemory(&ov[idx], sizeof(OVERLAPPED));
            ov[idx].hEvent = hEvent[idx];
            ok = 1;
            if (!ReadFile(ModuleHandle, ADC_Buf[idx], sizeof(ADC_Buf[idx]), NULL, &ov[idx])
                && (GetLastError() != ERROR_IO_PENDING))
                {
                f_ThreadMsg(TID, "ReadFile() failed, stopping ADC");
                ok = 0;
                }
            else
                {
                HANDLE WaitList[2];
                idx ^= 1;
                /* Ждем окончания предыдущего чтения или прихода команды */
                WaitList[0] = hControlEvent[TID];
                WaitList[1] = hEvent[idx];
                while (WaitForMultipleObjects(2, WaitList, 0, INFINITE) == WAIT_OBJECT_0)
                    {
                    /* Пришла команда */
                    if ((Control[TID] == CTL_TERMINATE) || (Control[TID] == CTL_TOGGLE)
                        || (Control[TID] == CTL_SLEEP))
                        {
                        CancelIo(ModuleHandle);
                        f_CloseHandles(2, hEvent);
                        CloseHandle(hFile);
                        EnterCriticalSection(&cs);
                        if (pModule->STOP_ADC())
                            {
                            f_ThreadMsg(TID, "ADC stopped");
                            }
                        else
                            {
                            f_ThreadMsg(TID, "Cannot stop ADC");
                            }
                        LeaveCriticalSection(&cs);
                        running = 0;
                        if (Control[TID] == CTL_SLEEP)
                            {
                            EnterCriticalSection(&cs);
                            if (pModule->PutArray(&bConst_1, 1, 0x430))
                                {
                                f_ThreadMsg(TID, "Sleep mode engaged");
                                }
                            else
                                {
                                f_ThreadMsg(TID, "Cannot enter sleep mode");
                                }
                            LeaveCriticalSection(&cs);
                            }
                        if (Control[TID] == CTL_TERMINATE)
                            return 0;
                        }
                    }
                ResetEvent(hEvent[idx]);
                if (running)
                    {
                    f_ThreadMsg(TID, "data...");
                    if (!GetOverlappedResult(ModuleHandle, &ov[idx], &TransferSize, FALSE))
                        {
                        f_ThreadMsg(TID, "Data stream interrupted, stopping ADC");
                        ok = 0;
                        }
                    if (!WriteFile(hFile, ADC_Buf[idx], TransferSize, &dummy, NULL))
                        {
                        f_ThreadMsg(TID, "File write error, stopping ADC");
                        ok = 0;
                        }
                    }
                } /* if ReadFile */
            if (!ok)
                {
                CancelIo(ModuleHandle);
                f_CloseHandles(2, hEvent);
                CloseHandle(hFile);
                EnterCriticalSection(&cs);
                pModule->STOP_ADC();
                LeaveCriticalSection(&cs);
                running = 0;
                }
            } /* if running */
        } /* for (;;) */
    return 0;
    }
/*------------------------------------------------------------------------------------------------*/

/*------------------------------------------------------------------------------------------------*/
DWORD WINAPI DAC_Thread(LPVOID)
    {
    const int TID = TID_DAC;
    int running = 0;
    int idx = 0;
    HANDLE hEvent[2] = {INVALID_HANDLE_VALUE, INVALID_HANDLE_VALUE };
    OVERLAPPED ov[2];

    for (;;)
        {
        if (!running)
            {
            WaitForSingleObject(hControlEvent[TID], INFINITE);
            switch (Control[TID])
                {
                case CTL_TERMINATE:      /* Завершение программы */
                    return 0; /* Ничего не открыто, так что просто выйти */
                case CTL_TOGGLE:        /* Запуск ЦАП */
                    EnterCriticalSection(&cs);
                    if (pModule->STOP_DAC() && pModule->SET_DAC_PARS(&dp) && pModule->START_DAC())
                        {
                        static short int level = 0x7FFF;
                        /* Заполняем массив ЦАП отсчетами синуса (канал 0) и треугольника (канал 1) с частотой 1 кГц */
                        for (int i = 0; i < DAC_BUF_SAMPLES; i++)
                            {
                            double x = (double)((1000 * i) % DAC_FREQ) / DAC_FREQ;
                            DAC_Buf[i][0] = (int)(level * sin(2 * M_PI * x));
                            DAC_Buf[i][1] = (int)(4 * level * (-0.5 + x - fabs(x - 0.25) + fabs(x - 0.75)));
                            }
#if FLIP_FLOP_AMP
                        level = level ^ 0x4000;
#endif
#if MARK_DAC_START
                        DAC_Buf[0][0] = DAC_Buf[0][1] = 0x7FFF;
#endif
                        hEvent[0] = CreateEvent(NULL, TRUE, FALSE, NULL);
                        hEvent[1] = CreateEvent(NULL, TRUE, FALSE, NULL);
                        ZeroMemory(&ov[0], sizeof(OVERLAPPED));
                        ov[0].hEvent = hEvent[0];
                        if (WriteFile(ModuleHandle, DAC_Buf, sizeof(DAC_Buf), NULL, &ov[0])
                            || (GetLastError() == ERROR_IO_PENDING))
                            {
                            idx = 1;
                            running = 1;
                            f_ThreadMsg(TID, "DAC started");
                            }
                        else
                            {
                            f_ThreadMsg(TID, "WriteFile() failed during start");
                            f_CloseHandles(2, hEvent);
                            pModule->STOP_DAC();
                            }
                        }
                    else
                        {
                        f_ThreadMsg(TID, "Cannot start DAC");
                        }
                    LeaveCriticalSection(&cs);
                    break;
                }
            }
        else /* running */
            {
            /* Ставим в очередь следующий буфер */
            ZeroMemory(&ov[idx], sizeof(OVERLAPPED));
            ov[idx].hEvent = hEvent[idx];
            if (WriteFile(ModuleHandle, DAC_Buf, sizeof(DAC_Buf), NULL, &ov[idx])
                || (GetLastError() == ERROR_IO_PENDING))
                {
                HANDLE WaitList[2];
                idx ^= 1;
                /* Ждем окончания предыдущей записи или прихода команды */
                WaitList[0] = hControlEvent[TID];
                WaitList[1] = hEvent[idx];
                while (WaitForMultipleObjects(2, WaitList, 0, INFINITE) == WAIT_OBJECT_0)
                    {
                    /* Пришла команда */
                    if ((Control[TID] == CTL_TERMINATE) || (Control[TID] == CTL_TOGGLE))
                        {
                        //WaitForSingleObject(hEvent[idx], INFINITE);
                        //WaitForSingleObject(hEvent[idx ^ 1], INFINITE);
                        CancelIo(ModuleHandle);
                        f_CloseHandles(2, hEvent);
                        EnterCriticalSection(&cs);
                        if (pModule->STOP_DAC())
                            {
                            f_ThreadMsg(TID, "DAC stopped");
                            }
                        else
                            {
                            f_ThreadMsg(TID, "Cannot stop DAC");
                            }
                        LeaveCriticalSection(&cs);
                        running = 0;
                        if (Control[TID] == CTL_TERMINATE)
                            return 0;
                        break;
                        }
                    }
                ResetEvent(hEvent[idx]);
                }
            else
                {
                f_ThreadMsg(TID, "WriteFile() failed, stopping DAC");
                CancelIo(ModuleHandle);
                f_CloseHandles(2, hEvent);
                EnterCriticalSection(&cs);
                pModule->STOP_DAC();
                LeaveCriticalSection(&cs);
                running = 0;
                }
            } /* if running */
        } /* for (;;) */
    return 0;
    }
/*------------------------------------------------------------------------------------------------*/

/*------------------------------------------------------------------------------------------------*/
void AbortProgram(const char *ErrorString, ...)
    {
    va_list va;

    if (pModule)
       pModule->ReleaseLInstance();
    if (ErrorString)
        {
        va_start(va, ErrorString);
        vprintf(ErrorString, va);
        va_end(va);
        }
    exit(0);
    }
/*------------------------------------------------------------------------------------------------*/

/*------------------------------------------------------------------------------------------------*/
int main()
    {
    DWORD DLL_Ver;
    int i;
    char ModuleName[32];
    MODULE_DESCRIPTION_E140 DevDesc;
    HANDLE hThread[3];
    HANDLE WaitList[3];

    printf("** E-140 Simultaneous ADC/DAC test **\n\n");

    /* Проверка версии Lusbapi.dll */
    DLL_Ver = GetDllVersion();
    if (DLL_Ver != CURRENT_VERSION_LUSBAPI)
        AbortProgram("Lusbapi.dll version mismatch (found %lu.%lu, need %u.%u)\n",
            DLL_Ver >> 16, DLL_Ver & 0xFFFF,
            CURRENT_VERSION_LUSBAPI >> 16, CURRENT_VERSION_LUSBAPI & 0xFFFF);

    /* Соединяемся с модулем */
    pModule = static_cast<ILE140 *>(CreateLInstance((char*)"e140"));
    if (!pModule)
        AbortProgram("Connection failed: Cannot create module interface.\n");
    for (i = 0; i < 127; i++)
        {
        if (pModule->OpenLDevice(i))
            break;
        }
    if (i == 127)
        AbortProgram("Connection failed: E-140 not found.\n");

    /* Получаем хэндл устройства, читаем имя и дескриптор устройства */
    ModuleHandle = pModule->GetModuleHandle();
    if (ModuleHandle == INVALID_HANDLE_VALUE)
        AbortProgram("GetModuleHandle() failed.\n");
    if (!pModule->GetModuleName(ModuleName))
        AbortProgram("GetModuleName() failed.\n");
    if (!pModule->GET_MODULE_DESCRIPTION(&DevDesc))
        AbortProgram("GET_MODULE_DESCRIPTION() failed.\n");

    printf("Connected to %s (S/N %s, Fosc = %.0f MHz).\n",
        ModuleName, DevDesc.Module.SerialNumber, (DevDesc.Mcu.ClockRate / 1000));
    printf("Ready to test with DAC frequency %u Hz, ADC frequency %u Hz.\n\n",
        DAC_FREQ, ADC_FREQ);

    /* Заполняем массив ЦАП отсчетами синуса (канал 0) и треугольника (канал 1) с частотой 1 кГц */
    for (i = 0; i < DAC_BUF_SAMPLES; i++)
        {
        double x = (double)((1000 * i) % DAC_FREQ) / DAC_FREQ;
        DAC_Buf[i][0] = (int)(0x7FFF * sin(2 * M_PI * x));
        DAC_Buf[i][1] = (int)(4 * 0x7FFF * (-0.5 + x - fabs(x - 0.25) + fabs(x - 0.75)));
        }
    
    /* Заполняем конфигурацию каналов АЦП */
    ap.ClkSource = 0;
    ap.EnableClkOutput = 0;
    ap.InputMode = NO_SYNC_E140;
    ap.SynchroAdType = 0; /* 0 = level, 1 = edge */
    ap.SynchroAdMode = 0; /* 0 = up, 1 = down */
    ap.SynchroAdChannel = CH_GAIN_1 | CH_MODE_DIFF | 0x0F;
    ap.SynchroAdPorog = 1000;
    ap.ChannelsQuantity = 2;
    ap.ControlTable[0] = CH_GAIN_1 | CH_MODE_DIFF | 0x00;
    ap.ControlTable[1] = CH_GAIN_1 | CH_MODE_DIFF | 0x01;
    ap.AdcRate = (double)ADC_FREQ / 1000.0;
    ap.InterKadrDelay = 0.0;

    /* Заполняем конфигурацию ЦАП */
    dp.SyncWithADC = 0;
    dp.SetZeroOnStop = ZERO_ON_STOP;
    dp.DacRate = (double)DAC_FREQ / 1000.0;

    /* Стираем все старые файлы данных */
    {
    HANDLE hFind;
    WIN32_FIND_DATA FindData;
    hFind = FindFirstFile("adc*.dat", &FindData);
    if (hFind != INVALID_HANDLE_VALUE)
        {
        do
            {
            DeleteFile(FindData.cFileName);
            }
        while (FindNextFile(hFind, &FindData));
        FindClose(hFind);
        }
    }

    /* Остановим ЦАП */
    if (!pModule->STOP_DAC())
        AbortProgram("Cannot stop DAC.\n");
    /* Остановим АЦП */
    if (!pModule->STOP_ADC())
        AbortProgram("Cannot stop ADC.\n");

    /* Создаем события для управления потоками */
    hControlEvent[TID_DAC] = CreateEvent(NULL, FALSE /* auto reset */, FALSE, NULL);
    hControlEvent[TID_ADC] = CreateEvent(NULL, FALSE /* auto reset */, FALSE, NULL);
    /* Создаем события для передачи сообщений */
    hThreadMsgEvent[TID_DAC] = CreateEvent(NULL, TRUE /* manual reset */, FALSE, NULL);
    hThreadMsgEvent[TID_ADC] = CreateEvent(NULL, TRUE /* manual reset */, FALSE, NULL);

    puts("[A]   - start/stop ADC");
    puts("[D]   - start/stop DAC");
    puts("[S]   - sleep (uses ADC thread)");
    puts("[Esc] - exit");
    while (kbhit()) getch();

    /* Создаем критическую секцию для обращения к модулю */
    InitializeCriticalSection(&cs);

    /* Создаем потоки записи в ЦАП, чтения из АЦП и управляющий */
    hThread[0] = CreateThread(0, 0x2000, DAC_Thread, NULL, 0, NULL);
    hThread[1] = CreateThread(0, 0x2000, ADC_Thread, NULL, 0, NULL);
    hThread[2] = CreateThread(0, 0x2000, ControlThread, NULL, 0, NULL);

    /* Цикл управления */
    WaitList[0] = hThread[2]; /* По завершению управляющего потока */
    WaitList[1] = hThreadMsgEvent[TID_DAC];
    WaitList[2] = hThreadMsgEvent[TID_ADC];

    for (;;)
        {
        switch (WaitForMultipleObjects(3, WaitList, 0, INFINITE))
            {
            case WAIT_OBJECT_0: /* Управляющий поток завершился */
                /* Дождаться завершения потоков АЦП и ЦАП */
                WaitForMultipleObjects(2, hThread, 1, INFINITE);
                f_PrintThreadMsg(TID_DAC, "DAC");
                f_PrintThreadMsg(TID_ADC, "ADC");
                f_CloseHandles(2, hThreadMsgEvent);
                f_CloseHandles(2, hControlEvent);
                AbortProgram("Done.\n");
                break;
            case WAIT_OBJECT_0 + 1:
                f_PrintThreadMsg(TID_DAC, "DAC");
                ResetEvent(hThreadMsgEvent[TID_DAC]);
                break;
            case WAIT_OBJECT_0 + 2:
                f_PrintThreadMsg(TID_ADC, "ADC");
                ResetEvent(hThreadMsgEvent[TID_ADC]);
                break;
            }
        }
    }
/*------------------------------------------------------------------------------------------------*/
/*================================================================================================*/
