#ifndef __LusbapiH__
#define __LusbapiH__

	// --------------------------------------------------------------------------
	// ---------------------------- COMMON PART ---------------------------------
	// --------------------------------------------------------------------------
	#include <windows.h>
	#include "LusbapiTypes.h"

	// версия библиотеки
	#define 	VERSION_MAJOR_LUSBAPI 			(0x3)   	// только одна цифра
	#define 	VERSION_MINOR_LUSBAPI 			(0x3)		// только одна цифра
	#define 	CURRENT_VERSION_LUSBAPI			((VERSION_MAJOR_LUSBAPI << 0x10) | VERSION_MINOR_LUSBAPI)

	#define InitLDevice(Slot) OpenLDevice(Slot)

	// экспортирукемые функции
	extern "C" DWORD WINAPI GetDllVersion(void);
	extern "C" LPVOID WINAPI CreateLInstance(PCHAR const DeviceName);

	// возможные индексы скорости работы модуля на шине USB
	enum { USB11_LUSBAPI, USB20_LUSBAPI, INVALID_USB_SPEED_LUSBAPI };
	// полное отсутствме модификиций модуля
	enum { NO_MODULE_MODIFICATION_LUSBAPI = -1 };
	// максимально возможное кол-во опрашиваемых виртуальных слотов
	const WORD MAX_VIRTUAL_SLOTS_QUANTITY_LUSBAPI = 127;


	// ==========================================================================
	// *************************** L-Card USB BASE ******************************
	// ==========================================================================
	struct ILUSBBASE
	{
		// функции общего назначения для работы с USB устройствами
		virtual BOOL WINAPI OpenLDevice(WORD VirtualSlot) = 0;
		virtual BOOL WINAPI CloseLDevice(void) = 0;
		virtual BOOL WINAPI ReleaseLInstance(void) = 0;
		// получение дескриптора устройства USB
		virtual HANDLE WINAPI GetModuleHandle(void) = 0;
		// получение названия используемого модуля
		virtual BOOL WINAPI GetModuleName(PCHAR const ModuleName) = 0;
		// получение текущей скорости работы шины USB
		virtual BOOL WINAPI GetUsbSpeed(BYTE * const UsbSpeed) = 0;
		// управления режимом низкого электропотребления модуля
		virtual BOOL WINAPI LowPowerMode(BOOL LowPowerFlag) = 0;
		// функция выдачи строки с последней ошибкой
		virtual BOOL WINAPI GetLastErrorInfo(LAST_ERROR_INFO_LUSBAPI * const LastErrorInfo) = 0;
	};




	// ==========================================================================
	// *************************** Модуль E14-140 *******************************
	// ==========================================================================
	// доступные индексы диапазонов входного напряжения модуля E14-140
	enum {	ADC_INPUT_RANGE_10000mV_E140, ADC_INPUT_RANGE_2500mV_E140, ADC_INPUT_RANGE_625mV_E140, ADC_INPUT_RANGE_156mV_E140, INVALID_ADC_INPUT_RANGE_E140 };
	// доступные индексы источника тактовых импульсов для АЦП
	enum {	INT_ADC_CLOCK_E140, EXT_ADC_CLOCK_E140, INVALID_ADC_CLOCK_E140 };
	// доступные индексы управления трансляцией тактовых импульсов АЦП
	// на линию SYN внешнего цифрового разъёма (только при внутреннем
	// источнике тактовых импульсоц АЦП)
	enum {	ADC_CLOCK_TRANS_DISABLED_E140, ADC_CLOCK_TRANS_ENABLED_E140, INVALID_ADC_CLOCK_TRANS_E140 };
	// возможные типы синхронизации модуля E14-140
	enum { 	NO_SYNC_E140, TTL_START_SYNC_E140, TTL_KADR_SYNC_E140, ANALOG_SYNC_E140, INVALID_SYNC_E140 };
	// возможные опции наличия микросхемы ЦАП
	enum {	DAC_INACCESSIBLED_E140, DAC_ACCESSIBLED_E140, INVALID_DAC_OPTION_E140 };
	// доступные индексы ревизий модуля E14-140
	enum {	REVISION_A_E140, REVISION_B_E140, INVALID_REVISION_E140 };
	// доступные индексы синхронизации потоковой работы ЦАП и АЦП
	enum {	DIS_ADC_DAC_SYNC_E140, ENA_ADC_DAC_SYNC_E140, INVALID_ADC_DAC_SYNC_E140 };
	// доступные индексы режимов остановки потокового ЦАП
	enum {	NORMAL_DAC_ON_STOP_E140, ZERO_DAC_ON_STOP_E140, INVALID_DAC_ON_STOP_E140 };

	// константы для работы с модулем
	enum 	{
				MAX_CONTROL_TABLE_LENGTH_E140 = 128,
				ADC_INPUT_RANGES_QUANTITY_E140 = INVALID_ADC_INPUT_RANGE_E140,
				ADC_CALIBR_COEFS_QUANTITY_E140 = ADC_INPUT_RANGES_QUANTITY_E140,
				DAC_CHANNELS_QUANTITY_E140 = 0x2, DAC_CALIBR_COEFS_QUANTITY_E140 = DAC_CHANNELS_QUANTITY_E140,
				TTL_LINES_QUANTITY_E140 = 0x10,	  		// кол-во цифровых линий
				USER_FLASH_SIZE_E140 = 0x200,   			// размер области пользовательского ППЗУ в байтах
				REVISIONS_QUANTITY_E140 = INVALID_REVISION_E140,		// кол-во ревизий (модификаций) модуля
			};
	// диапазоны входного напряжения АЦП в В
	const double ADC_INPUT_RANGES_E140[ADC_INPUT_RANGES_QUANTITY_E140] =
	{
		10.0, 10.0/4.0, 10.0/16.0, 10.0/64.0
	};
	// диапазоны выходного напряжения ЦАП в В
	const double DAC_OUTPUT_RANGE_E140 = 5.0;
	// доступные ревизии модуля
	const BYTE REVISIONS_E140[REVISIONS_QUANTITY_E140] = { 'A', 'B' };

	#pragma pack(1)
	// структура с информацией об модуле E14-140
	struct MODULE_DESCRIPTION_E140
	{
		MODULE_INFO_LUSBAPI     Module;		// общая информация о модуле
		INTERFACE_INFO_LUSBAPI  Interface;	// информация об используемом интерфейсе
		MCU_INFO_LUSBAPI<VERSION_INFO_LUSBAPI>		Mcu;	// информация о микроконтроллере
		ADC_INFO_LUSBAPI        Adc;			// информация о АЦП
		DAC_INFO_LUSBAPI        Dac;			// информация о ЦАП
		DIGITAL_IO_INFO_LUSBAPI DigitalIo;	// информация о цифровом вводе-выводе
	};
	// структура пользовательского ППЗУ модуля E14-140
	struct USER_FLASH_E140
	{
		BYTE Buffer[USER_FLASH_SIZE_E140];
	};
	// структура, задающая режим работы АЦП для модуля E14-140
	struct ADC_PARS_E140
	{
		WORD ClkSource;							// источник тактовых импульсов для запуска АПП
		WORD EnableClkOutput;					// разрешение трансляции тактовых импульсов запуска АЦП
		WORD InputMode;							// режим ввода даных с АЦП
		WORD SynchroAdType;						// тип аналоговой синхронизации
		WORD SynchroAdMode; 						// режим аналоговой сихронизации
		WORD SynchroAdChannel;  				// канал АЦП при аналоговой синхронизации
		SHORT SynchroAdPorog; 					// порог срабатывания АЦП при аналоговой синхронизации
		WORD ChannelsQuantity;					// число активных каналов
		WORD ControlTable[128];					// управляющая таблица с активными каналами
		double AdcRate;							// частота работы АЦП в кГц
		double InterKadrDelay;					// межкадровая задержка в мс
		double KadrRate;							// частота кадра в кГц
	};
	// структура, задающая режим потоковой работы ЦАП для модуля E14-140
	struct DAC_PARS_E140
	{
		BYTE SyncWithADC;							// 0 = обычный пуск ЦАП; !0 = синхронизировать с пуском АЦП
		BYTE SetZeroOnStop;						// !0 = при остановке потокового вывода установить на выходе ЦАП 0 В
		double DacRate;							// частота работы ЦАП в кГц
	};
	#pragma pack()

	//-----------------------------------------------------------------------------
	// интерфейс для модуля E14-140
	//-----------------------------------------------------------------------------
	struct ILE140 : public ILUSBBASE
	{
		// функции для работы с АЦП
		virtual BOOL WINAPI GET_ADC_PARS(ADC_PARS_E140 * const AdcPars) = 0;
		virtual BOOL WINAPI SET_ADC_PARS(ADC_PARS_E140 * const AdcPars) = 0;
		virtual BOOL WINAPI START_ADC(void) = 0;
		virtual BOOL WINAPI STOP_ADC(void) = 0;
		virtual BOOL WINAPI ADC_KADR(SHORT * const Data) = 0;
		virtual BOOL WINAPI ADC_SAMPLE(SHORT * const AdcData, WORD AdcChannel) = 0;
		virtual BOOL WINAPI ReadData(IO_REQUEST_LUSBAPI * const ReadRequest) = 0;

		// функции для работы с ЦАП
		virtual BOOL WINAPI GET_DAC_PARS(DAC_PARS_E140 * const DacPars) = 0;
		virtual BOOL WINAPI SET_DAC_PARS(DAC_PARS_E140 * const DacPars) = 0;
		virtual BOOL WINAPI START_DAC(void) = 0;
		virtual BOOL WINAPI STOP_DAC(void) = 0;
		virtual BOOL WINAPI WriteData(IO_REQUEST_LUSBAPI * const WriteRequest) = 0;
		virtual BOOL WINAPI DAC_SAMPLE(SHORT * const DacData, WORD DacChannel) = 0;
		virtual BOOL WINAPI DAC_SAMPLES(SHORT * const DacData1, SHORT * const DacData2) = 0;

		// функции для работы с ТТЛ линиями
		virtual BOOL WINAPI ENABLE_TTL_OUT(BOOL EnableTtlOut) = 0;
		virtual BOOL WINAPI TTL_IN(WORD * const TtlIn) = 0;
		virtual BOOL WINAPI TTL_OUT(WORD TtlOut) = 0;

		// функции для работы с пользовательской информацией ППЗУ
		virtual BOOL WINAPI ENABLE_FLASH_WRITE(BOOL IsUserFlashWriteEnabled) = 0;
		virtual BOOL WINAPI READ_FLASH_ARRAY(USER_FLASH_E140 * const UserFlash) = 0;
		virtual BOOL WINAPI WRITE_FLASH_ARRAY(USER_FLASH_E140 * const UserFlash) = 0;

		// функции для работы со служебной информацией ППЗУ
		virtual BOOL WINAPI GET_MODULE_DESCRIPTION(MODULE_DESCRIPTION_E140 * const ModuleDescription) = 0;
		virtual BOOL WINAPI SAVE_MODULE_DESCRIPTION(MODULE_DESCRIPTION_E140 * const ModuleDescription) = 0;

		// функции для прямого досупа к микроконтроллеру
		virtual BOOL WINAPI GetArray(BYTE * const Buffer, WORD Size, WORD Address) = 0;
		virtual BOOL WINAPI PutArray(BYTE * const Buffer, WORD Size, WORD Address) = 0;
	};





	// ==========================================================================
	// *************************** Модуль E-154 *******************************
	// ==========================================================================
	// доступные индексы диапазонов входного напряжения модуля E-154
	enum {	ADC_INPUT_RANGE_5000mV_E154, ADC_INPUT_RANGE_1600mV_E154, ADC_INPUT_RANGE_500mV_E154, ADC_INPUT_RANGE_160mV_E154, INVALID_ADC_INPUT_RANGE_E154 };
	// доступные индексы источника тактовых импульсов для АЦП, сохранены для совместимости с E14-140
	enum {	INT_ADC_CLOCK_E154, EXT_ADC_CLOCK_E154, INVALID_ADC_CLOCK_E154 };
	// доступные индексы управления трансляцией тактовых импульсов АЦП
	// на линию SYN внешнего цифрового разъёма (только при внутреннем
	// источнике тактовых импульсоц АЦП),   сохранены для совместимости с E14-140
	enum {	ADC_CLOCK_TRANS_DISABLED_E154, ADC_CLOCK_TRANS_ENABLED_E154, INVALID_ADC_CLOCK_TRANS_E154 };
	// возможные типы синхронизации модуля E-154
	enum { 	NO_SYNC_E154, TTL_START_SYNC_E154, TTL_KADR_SYNC_E154, ANALOG_SYNC_E154, INVALID_SYNC_E154 };
	// возможные опции наличия микросхемы ЦАП
	enum {	DAC_INACCESSIBLED_E154, DAC_ACCESSIBLED_E154, INVALID_DAC_OPTION_E154 };
	// доступные индексы ревизий модуля E-154
	enum {	REVISION_A_E154, INVALID_REVISION_E154 };

	// константы для работы с модулем
	enum 	{
				MAX_CONTROL_TABLE_LENGTH_E154 = 16,
				ADC_INPUT_RANGES_QUANTITY_E154 = INVALID_ADC_INPUT_RANGE_E154,
				ADC_CALIBR_COEFS_QUANTITY_E154 = ADC_INPUT_RANGES_QUANTITY_E154,
				DAC_CHANNELS_QUANTITY_E154 = 0x1, DAC_CALIBR_COEFS_QUANTITY_E154 = DAC_CHANNELS_QUANTITY_E154,
				TTL_LINES_QUANTITY_E154 = 0x08,	  		// кол-во цифровых линий
				USER_FLASH_SIZE_E154 = 0x80,   			// размер области пользовательского ППЗУ в байтах
				REVISIONS_QUANTITY_E154 = INVALID_REVISION_E154,		// кол-во ревизий (модификаций) модуля
			};
	// диапазоны входного напряжения АЦП в В
	const double ADC_INPUT_RANGES_E154[ADC_INPUT_RANGES_QUANTITY_E154] =
	{
		5.0, 1.6, 0.5, 0.16
	};
	// диапазоны выходного напряжения ЦАП в В
	const double DAC_OUTPUT_RANGE_E154 = 5.0;
	// доступные ревизии модуля
	const BYTE REVISIONS_E154[REVISIONS_QUANTITY_E154] = { 'A' };

	#pragma pack(1)
	// структура с информацией об модуле E-154
	struct MODULE_DESCRIPTION_E154
	{
		MODULE_INFO_LUSBAPI     Module;		// общая информация о модуле
		INTERFACE_INFO_LUSBAPI  Interface;	// информация об используемом интерфейсе
		MCU_INFO_LUSBAPI<VERSION_INFO_LUSBAPI>		Mcu;	// информация о микроконтроллере
		ADC_INFO_LUSBAPI        Adc;			// информация о АЦП
		DAC_INFO_LUSBAPI        Dac;			// информация о ЦАП
		DIGITAL_IO_INFO_LUSBAPI DigitalIo;	// информация о цифровом вводе-выводе
	};
	// структура, задающая режим работы АЦП для модуля E14-154
	struct ADC_PARS_E154
	{
		WORD ClkSource;							// источник тактовых импульсов для запуска АПП
		WORD EnableClkOutput;					// разрешение трансляции тактовых импульсов запуска АЦП
		WORD InputMode;							// режим ввода даных с АЦП
		WORD SynchroAdType;						// тип аналоговой синхронизации
		WORD SynchroAdMode; 						// режим аналоговой сихронизации
		WORD SynchroAdChannel;  				// канал АЦП при аналоговой синхронизации
		SHORT SynchroAdPorog; 					// порог срабатывания АЦП при аналоговой синхронизации
		WORD ChannelsQuantity;					// число активных каналов
		WORD ControlTable[16];					// управляющая таблица с активными каналами
		double AdcRate;	  			  			// частота работы АЦП в кГц
		double InterKadrDelay;		  			// межкадровая задержка в мс
		double KadrRate;							// частота кадра в кГц
	};

	#pragma pack()

	//-----------------------------------------------------------------------------
	// интерфейс для модуля E14-154
	//-----------------------------------------------------------------------------
	struct ILE154 : public ILUSBBASE
	{
		// функции для работы с АЦП
		virtual BOOL WINAPI GET_ADC_PARS(ADC_PARS_E154 * const AdcPars) = 0;
 		virtual BOOL WINAPI SET_ADC_PARS(ADC_PARS_E154 * const AdcPars) = 0;
		virtual BOOL WINAPI START_ADC(void) = 0;
		virtual BOOL WINAPI STOP_ADC(void) = 0;
		virtual BOOL WINAPI ADC_KADR(SHORT * const Data) = 0;
		virtual BOOL WINAPI ADC_SAMPLE(SHORT * const AdcData, WORD AdcChannel) = 0;
		virtual BOOL WINAPI ReadData(IO_REQUEST_LUSBAPI * const ReadRequest) = 0;
		virtual BOOL WINAPI ProcessArray(SHORT *src, double *dest, DWORD size, BOOL calibr, BOOL volt) = 0;
		virtual BOOL WINAPI ProcessOnePoint(SHORT src, double *dest, DWORD channel, BOOL calibr, BOOL volt) = 0;
		virtual BOOL WINAPI FIFO_STATUS(DWORD *FifoOverflowFlag, double *FifoMaxPercentLoad, DWORD *FifoSize, DWORD *MaxFifoBytesUsed) = 0;

		// функции для работы с ЦАП
		virtual BOOL WINAPI DAC_SAMPLE(SHORT * const DacData, WORD DacChannel) = 0;
		virtual BOOL WINAPI DAC_SAMPLE_VOLT(double  const DacData, BOOL calibr) = 0;

		// функции для работы с ТТЛ линиями
		virtual BOOL WINAPI ENABLE_TTL_OUT(BOOL EnableTtlOut) = 0;
		virtual BOOL WINAPI TTL_IN(WORD * const TtlIn) = 0;
		virtual BOOL WINAPI TTL_OUT(WORD TtlOut) = 0;

		// функции для работы с пользовательской информацией ППЗУ
		virtual BOOL WINAPI ENABLE_FLASH_WRITE(BOOL IsUserFlashWriteEnabled) = 0;
		virtual BOOL WINAPI READ_FLASH_ARRAY(BYTE * const UserFlash) = 0;
		virtual BOOL WINAPI WRITE_FLASH_ARRAY(BYTE * const UserFlash) = 0;

		// функции для работы со служебной информацией ППЗУ
		virtual BOOL WINAPI GET_MODULE_DESCRIPTION(MODULE_DESCRIPTION_E154 * const ModuleDescription) = 0;
		virtual BOOL WINAPI SAVE_MODULE_DESCRIPTION(MODULE_DESCRIPTION_E154 * const ModuleDescription) = 0;

		// функции для прямого досупа к микроконтроллеру
		virtual BOOL WINAPI GetArray(BYTE * const Buffer, WORD Size, WORD Address) = 0;
		virtual BOOL WINAPI PutArray(BYTE * const Buffer, WORD Size, WORD Address) = 0;

	};




	// ==========================================================================
	// *************************** Модуль E14-440 *******************************
	// ==========================================================================
	// доступные состояния сброса модуля E14-440
	enum {	INIT_E440, RESET_E440, INVALID_RESET_TYPE_E440 };
	// доступные индексы источника тактовых импульсов для АЦП
	enum	{	INT_ADC_CLOCK_E440, INT_ADC_CLOCK_WITH_TRANS_E440, EXT_ADC_CLOCK_E440, INVALID_ADC_CLOCK_E440 };
	// доступные индексы диапазонов входного напряжения модуля E14-440
	enum {	ADC_INPUT_RANGE_10000mV_E440, ADC_INPUT_RANGE_2500mV_E440, ADC_INPUT_RANGE_625mV_E440, ADC_INPUT_RANGE_156mV_E440, INVALID_ADC_INPUT_RANGE_E440 };
	// возможные типы синхронизации модуля E14-440
	enum {	NO_SYNC_E440, TTL_START_SYNC_E440, TTL_KADR_SYNC_E440, ANALOG_SYNC_E440, INVALID_SYNC_E440 };
	// возможные опции наличия микросхемы ЦАП
	enum {	DAC_INACCESSIBLED_E440, DAC_ACCESSIBLED_E440, INVALID_DAC_OPTION_E440 };
	// возможные типы DSP (сейчас только ADSP-2185)
	enum {	ADSP2184_E440, ADSP2185_E440, ADSP2186_E440, INVALID_DSP_TYPE_E440 };
	// возможные тактовые частоты модудя (сейчас только 24000 кГц)
	enum {	F14745_E440, F16667_E440, F20000_E440, F24000_E440, INVALID_QUARTZ_FREQ_E440 };
	// доступные индексы ревизий модуля E14-440
	enum	{	REVISION_A_E440, REVISION_B_E440, REVISION_C_E440, REVISION_D_E440, REVISION_E_E440, REVISION_F_E440, INVALID_REVISION_E440 };

	// константы для работы с модулем
	enum 	{
				MAX_CONTROL_TABLE_LENGTH_E440 = 128,
				ADC_INPUT_RANGES_QUANTITY_E440 = INVALID_ADC_INPUT_RANGE_E440,
				ADC_CALIBR_COEFS_QUANTITY_E440 = ADC_INPUT_RANGES_QUANTITY_E440,
				MAX_ADC_FIFO_SIZE_E440 = 0x3000,			// 12288
				DAC_CHANNELS_QUANTITY_E440 = 0x2, DAC_CALIBR_COEFS_QUANTITY_E440 = DAC_CHANNELS_QUANTITY_E440,
				MAX_DAC_FIFO_SIZE_E440 = 0x0FC0,			// 4032
				TTL_LINES_QUANTITY_E440 = 0x10, 			// кол-во цифровых линий
				REVISIONS_QUANTITY_E440 = INVALID_REVISION_E440,		// кол-во ревизий (модификаций) модуля
			};
	// диапазоны входного напряжения АЦП в В
	const double ADC_INPUT_RANGES_E440[ADC_INPUT_RANGES_QUANTITY_E440] =
	{
		10.0, 10.0/4.0, 10.0/16.0, 10.0/64.0
	};
	// диапазоны выходного напряжения ЦАП в В
	const double DAC_OUTPUT_RANGE_E440 = 5.0;
	// доступные ревизии модуля
	const BYTE REVISIONS_E440[REVISIONS_QUANTITY_E440] = { 'A', 'B', 'C', 'D', 'E', 'F' };

	#pragma pack(1)
	// структура с информацией об модуле E14-440
	struct MODULE_DESCRIPTION_E440
	{
		MODULE_INFO_LUSBAPI     Module;		// общая информация о модуле
		INTERFACE_INFO_LUSBAPI  Interface;	// информация об используемом интерфейсе
		MCU_INFO_LUSBAPI<VERSION_INFO_LUSBAPI>		Mcu;	// информация о микроконтроллере
		DSP_INFO_LUSBAPI        Dsp;			// информация о DSP
		ADC_INFO_LUSBAPI        Adc;			// информация о АЦП
		DAC_INFO_LUSBAPI        Dac;			// информация о ЦАП
		DIGITAL_IO_INFO_LUSBAPI DigitalIo;	// информация о цифровом вводе-выводе
	};
	// структура, задающая режим работы АЦП для модуля E-440
	struct ADC_PARS_E440
	{
		BOOL IsAdcEnabled;		 			// статус работы АЦП (только при чтении)
		BOOL IsCorrectionEnabled;			// управление разрешением корректировкой данных на уровне драйвера DSP
		WORD AdcClockSource;					// источник тактовых импульсов запуска АЦП: внутренние или внешние
		WORD InputMode;						// режим ввода даных с АЦП
		WORD SynchroAdType;					// тип аналоговой синхронизации
		WORD SynchroAdMode; 					// режим аналоговой сихронизации
		WORD SynchroAdChannel;  			// канал АЦП при аналоговой синхронизации
		SHORT SynchroAdPorog; 				// порог срабатывания АЦП при аналоговой синхронизации
		WORD ChannelsQuantity;				// число активных каналов
		WORD ControlTable[MAX_CONTROL_TABLE_LENGTH_E440];		// управляющая таблица с активными каналами
		double AdcRate;	  			  		// частота работы АЦП в кГц
		double InterKadrDelay;		  		// Межкадровая задержка в мс
		double KadrRate;					// частота кадра в кГц
		WORD AdcFifoBaseAddress;			// базовый адрес FIFO буфера АЦП
		WORD AdcFifoLength;					// длина FIFO буфера АЦП
		double AdcOffsetCoefs[ADC_CALIBR_COEFS_QUANTITY_E440];	// смещение	АЦП: 4диапазона
		double AdcScaleCoefs[ADC_CALIBR_COEFS_QUANTITY_E440];		// масштаб АЦП	: 4диапазона
	};

	// структура, задающая режим работы ЦАП для модуля E-440
	struct DAC_PARS_E440
	{
		BOOL DacEnabled;						// разрешение/запрещение работы ЦАП
		double DacRate;	  			  		// частота работы ЦАП в кГц
		WORD DacFifoBaseAddress;			// базовый адрес FIFO буфера ЦАП
		WORD DacFifoLength;					// длина FIFO буфера ЦАП
	};
	#pragma pack()

	// адрес начала сегмента блока данных в памяти программ драйвера DSP
	const WORD DataBaseAddress_E440 = 0x30;
	// переменные штатного LBIOS для модуля E14-440 (раполагаются в памяти программ DSP)
	#define 	  	L_PROGRAM_BASE_ADDRESS_E440				(DataBaseAddress_E440 + 0x0)
	#define 	  	L_READY_E440 									(DataBaseAddress_E440 + 0x1)
	#define	  	L_TMODE1_E440 									(DataBaseAddress_E440 + 0x2)
	#define	  	L_TMODE2_E440 									(DataBaseAddress_E440 + 0x3)
	#define	  	L_TEST_LOAD_E440	 							(DataBaseAddress_E440 + 0x4)
	#define	  	L_COMMAND_E440	 			      			(DataBaseAddress_E440 + 0x5)

	#define		L_DAC_SCLK_DIV_E440							(DataBaseAddress_E440 + 0x7)
	#define		L_DAC_RATE_E440								(DataBaseAddress_E440 + 0x8)
	#define	  	L_ADC_RATE_E440  			      			(DataBaseAddress_E440 + 0x9)
	#define		L_ADC_ENABLED_E440	 						(DataBaseAddress_E440 + 0xA)
	#define		L_ADC_FIFO_BASE_ADDRESS_E440				(DataBaseAddress_E440 + 0xB)
	#define		L_CUR_ADC_FIFO_LENGTH_E440					(DataBaseAddress_E440 + 0xC)
	#define		L_ADC_FIFO_LENGTH_E440						(DataBaseAddress_E440 + 0xE)
	#define		L_CORRECTION_ENABLED_E440					(DataBaseAddress_E440 + 0xF)
	#define		L_LBIOS_VERSION_E440							(DataBaseAddress_E440 + 0x10)
	#define		L_ADC_SAMPLE_E440								(DataBaseAddress_E440 + 0x11)
	#define		L_ADC_CHANNEL_E440	 						(DataBaseAddress_E440 + 0x12)
	#define		L_INPUT_MODE_E440								(DataBaseAddress_E440 + 0x13)
	#define		L_SYNCHRO_AD_CHANNEL_E440					(DataBaseAddress_E440 + 0x16)
	#define		L_SYNCHRO_AD_POROG_E440						(DataBaseAddress_E440 + 0x17)
	#define		L_SYNCHRO_AD_MODE_E440 						(DataBaseAddress_E440 + 0x18)
	#define		L_SYNCHRO_AD_TYPE_E440 						(DataBaseAddress_E440 + 0x19)

	#define		L_CONTROL_TABLE_LENGHT_E440				(DataBaseAddress_E440 + 0x1B)
	#define		L_FIRST_SAMPLE_DELAY_E440					(DataBaseAddress_E440 + 0x1C)
	#define		L_INTER_KADR_DELAY_E440						(DataBaseAddress_E440 + 0x1D)

	#define		L_DAC_SAMPLE_E440								(DataBaseAddress_E440 + 0x20)
	#define		L_DAC_ENABLED_E440					 		(DataBaseAddress_E440 + 0x21)
	#define		L_DAC_FIFO_BASE_ADDRESS_E440				(DataBaseAddress_E440 + 0x22)
	#define		L_CUR_DAC_FIFO_LENGTH_E440					(DataBaseAddress_E440 + 0x24)
	#define		L_DAC_FIFO_LENGTH_E440						(DataBaseAddress_E440 + 0x25)

	#define		L_FLASH_ENABLED_E440 						(DataBaseAddress_E440 + 0x26)
	#define		L_FLASH_ADDRESS_E440 						(DataBaseAddress_E440 + 0x27)
	#define		L_FLASH_DATA_E440 							(DataBaseAddress_E440 + 0x28)

	#define		L_ENABLE_TTL_OUT_E440						(DataBaseAddress_E440 + 0x29)
	#define		L_TTL_OUT_E440									(DataBaseAddress_E440 + 0x2A)
	#define		L_TTL_IN_E440									(DataBaseAddress_E440 + 0x2B)

	#define		L_ADC_CLOCK_SOURCE_E440						(DataBaseAddress_E440 + 0x2F)

	#define		L_SCALE_E440									(DataBaseAddress_E440 + 0x30)
	#define		L_ZERO_E440										(DataBaseAddress_E440 + 0x34)

	#define		L_CONTROL_TABLE_E440							(0x80)

	#define		L_DSP_INFO_STUCTURE_E440					(0x200)

	//-----------------------------------------------------------------------------
	// интерфейс модуля E14-440
	//-----------------------------------------------------------------------------
	struct ILE440 : public ILUSBBASE
	{
		// функции работы с DSP
		virtual BOOL WINAPI RESET_MODULE(BYTE ResetFlag = INIT_E440) = 0;
		virtual BOOL WINAPI LOAD_MODULE(PCHAR const FileName = NULL) = 0;
		virtual BOOL WINAPI TEST_MODULE(void) = 0;
		virtual BOOL WINAPI SEND_COMMAND(WORD Command) = 0;

		// функции для работы с АЦП
		virtual BOOL WINAPI GET_ADC_PARS(ADC_PARS_E440 * const AdcPars) = 0;
		virtual BOOL WINAPI SET_ADC_PARS(ADC_PARS_E440 * const AdcPars) = 0;
		virtual BOOL WINAPI START_ADC(void) = 0;
		virtual BOOL WINAPI STOP_ADC(void) = 0;
		virtual BOOL WINAPI ADC_KADR(SHORT * const Data) = 0;
		virtual BOOL WINAPI ADC_SAMPLE(SHORT * const AdcData, WORD AdcChannel) = 0;
		virtual BOOL WINAPI ReadData(IO_REQUEST_LUSBAPI * const ReadRequest) = 0;

		// функции для работы с ЦАП
		virtual BOOL WINAPI GET_DAC_PARS(DAC_PARS_E440 * const DacPars) = 0;
		virtual BOOL WINAPI SET_DAC_PARS(DAC_PARS_E440 * const DacPars) = 0;
		virtual BOOL WINAPI START_DAC(void) = 0;
		virtual BOOL WINAPI STOP_DAC(void) = 0;
		virtual BOOL WINAPI WriteData(IO_REQUEST_LUSBAPI * const WriteRequest) = 0;
		virtual BOOL WINAPI DAC_SAMPLE(SHORT * const DacData, WORD DacChannel) = 0;

		// функции для работы с цифровыми линиями
		virtual BOOL WINAPI ENABLE_TTL_OUT(BOOL EnableTtlOut) = 0;
		virtual BOOL WINAPI TTL_IN(WORD * const TtlIn) = 0;
		virtual BOOL WINAPI TTL_OUT(WORD TtlOut) = 0;

		// функции для работы пользовательским ППЗУ модуля
		virtual BOOL WINAPI ENABLE_FLASH_WRITE(BOOL EnableFlashWrite) = 0;
		virtual BOOL WINAPI READ_FLASH_WORD(WORD FlashAddress, SHORT * const FlashWord) = 0;
		virtual BOOL WINAPI WRITE_FLASH_WORD(WORD FlashAddress, SHORT FlashWord) = 0;

		// функции для работы со служебной информацией из ППЗУ
		virtual BOOL WINAPI GET_MODULE_DESCRIPTION(MODULE_DESCRIPTION_E440 * const ModuleDescription) = 0;
		virtual BOOL WINAPI SAVE_MODULE_DESCRIPTION(MODULE_DESCRIPTION_E440 * const ModuleDescription) = 0;

		// функции для работы с памятью DSP
		virtual BOOL WINAPI PUT_LBIOS_WORD(WORD Address, SHORT Data) = 0;
		virtual BOOL WINAPI GET_LBIOS_WORD(WORD Address, SHORT * const Data) = 0;
		virtual BOOL WINAPI PUT_DM_WORD(WORD Address, SHORT Data) = 0;
		virtual BOOL WINAPI GET_DM_WORD(WORD Address, SHORT * const Data) = 0;
		virtual BOOL WINAPI PUT_PM_WORD(WORD Address, long Data) = 0;
		virtual BOOL WINAPI GET_PM_WORD(WORD Address, long * const Data) = 0;
		virtual BOOL WINAPI PUT_DM_ARRAY(WORD BaseAddress, WORD NPoints, SHORT * const Data) = 0;
		virtual BOOL WINAPI GET_DM_ARRAY(WORD BaseAddress, WORD NPoints, SHORT * const Data) = 0;
		virtual BOOL WINAPI PUT_PM_ARRAY(WORD BaseAddress, WORD NPoints, long * const Data) = 0;
		virtual BOOL WINAPI GET_PM_ARRAY(WORD BaseAddress, WORD NPoints, long * const Data) = 0;

		// функции для работы с загрузочным ППЗУ модуля
		virtual BOOL WINAPI ERASE_BOOT_FLASH(void) = 0;
		virtual BOOL WINAPI PUT_ARRAY_BOOT_FLASH(DWORD BaseAddress, DWORD NBytes, BYTE *Data) = 0;
		virtual BOOL WINAPI GET_ARRAY_BOOT_FLASH(DWORD BaseAddress, DWORD NBytes, BYTE *Data) = 0;
	};




	// ==========================================================================
	// *************************** Модуль E20-10 ********************************
	// ==========================================================================
	// доступные индексы источника сигнала старта сбора данных
	enum {
				INT_ADC_START_E2010, INT_ADC_START_WITH_TRANS_E2010,
				EXT_ADC_START_ON_RISING_EDGE_E2010, EXT_ADC_START_ON_FALLING_EDGE_E2010,
//				EXT_ADC_START_ON_HIGH_LEVEL_E2010, EXT_ADC_START_ON_LOW_LEVEL_E2010,		// для Rev.B и выше (пока нет)
				INVALID_ADC_START_E2010
			};
	// доступные индексы источника тактовых импульсов для запуска АЦП
	enum {	INT_ADC_CLOCK_E2010, INT_ADC_CLOCK_WITH_TRANS_E2010, EXT_ADC_CLOCK_ON_RISING_EDGE_E2010, EXT_ADC_CLOCK_ON_FALLING_EDGE_E2010, INVALID_ADC_CLOCK_E2010 };
	// возможные типы аналоговой синхронизации ввода данных (для Rev.B и выше)
	enum {
				NO_ANALOG_SYNCHRO_E2010,			// отсутствие аналоговой синхронизации
				ANALOG_SYNCHRO_ON_RISING_CROSSING_E2010, ANALOG_SYNCHRO_ON_FALLING_CROSSING_E2010,	// аналоговая синхронизация по переходу
				ANALOG_SYNCHRO_ON_HIGH_LEVEL_E2010, ANALOG_SYNCHRO_ON_LOW_LEVEL_E2010,		// аналоговая синхронизация по уровню
				INVALID_ANALOG_SYNCHRO_E2010
			};
	// доступные индексы диапазонов входного напряжения модуля E20-10
	enum {	ADC_INPUT_RANGE_3000mV_E2010, ADC_INPUT_RANGE_1000mV_E2010, ADC_INPUT_RANGE_300mV_E2010, INVALID_ADC_INPUT_RANGE_E2010 };
	// возможные типы подключения входного тракта модуля E20-10
	enum {	ADC_INPUT_ZERO_E2010, ADC_INPUT_SIGNAL_E2010, INVALID_ADC_INPUT_E2010 };
	// возможные индексы для управления входным током смещения модуля E20-10 (для Rev.B и выше)
	enum {	INPUT_CURRENT_OFF_E2010, INPUT_CURRENT_ON_E2010, INVALID_INPUT_CURRENT_E2010 };
	// возможные режимы фиксации факта перегрузки входных каналов при сборе данных (только для Rev.A)
	enum {	CLIPPING_OVERLOAD_E2010, MARKER_OVERLOAD_E2010, INVALID_OVERLOAD_E2010 };
	// доступные номера битов ошибок при выполнении сбора данных с АЦП
	enum {
				// битовое поле BufferOverrun структуры DATA_STATE_E2010
				BUFFER_OVERRUN_E2010 = 0x0,		// переполнение внутреннего буфера модуля
				// битовое поле ChannelsOverFlow структуры DATA_STATE_E2010 (для Rev.B и выше)
				OVERFLOW_OF_CHANNEL_1_E2010 = 0x0, OVERFLOW_OF_CHANNEL_2_E2010,	// биты локальных признаков переполнения разрядной сетки соответствующего канала
				OVERFLOW_OF_CHANNEL_3_E2010, OVERFLOW_OF_CHANNEL_4_E2010,			// за время выполнения одного запроса сбора данных ReadData()
				OVERFLOW_E2010 = 0x7					// бит глобального признака факта переполнения разрядной сетки модуля за всё время сбора данных от момента START_ADC() до STOP_ADC()
			};
	// возможные опции наличия микросхемы ЦАП для модуля E20-10
	enum {	DAC_INACCESSIBLED_E2010, DAC_ACCESSIBLED_E2010, INVALID_DAC_OPTION_E2010 };
	// доступные индексы ревизий модуля E20-10
	enum {	REVISION_A_E2010, REVISION_B_E2010, INVALID_REVISION_E2010 };
	// доступные индексы модификиций модуля E20-10
	enum {	BASE_MODIFICATION_E2010, 			// полоса входных частот 1.25 МГц
				F5_MODIFICATION_E2010, 				// полоса входных частот 5.00 МГц
				INVALID_MODIFICATION_E2010 };

	// доступные битовые константы для задания тестовых режимов работы модуля E20-10
	enum { NO_TEST_MODE_E2010, TEST_MODE_1_E2010 };

	// константы для работы с модулем
	enum 	{
				ADC_CHANNELS_QUANTITY_E2010 = 0x4, MAX_CONTROL_TABLE_LENGTH_E2010 = 256,
				ADC_INPUT_RANGES_QUANTITY_E2010 = INVALID_ADC_INPUT_RANGE_E2010,
				ADC_INPUT_TYPES_QUANTITY_E2010 = INVALID_ADC_INPUT_E2010,
				ADC_CALIBR_COEFS_QUANTITY_E2010 = ADC_CHANNELS_QUANTITY_E2010 * ADC_INPUT_RANGES_QUANTITY_E2010,
				DAC_CHANNELS_QUANTITY_E2010 = 0x2, DAC_CALIBR_COEFS_QUANTITY_E2010 = DAC_CHANNELS_QUANTITY_E2010,
				TTL_LINES_QUANTITY_E2010 = 0x10,		// кол-во входных и выходных цифровых линий
				USER_FLASH_SIZE_E2010 = 0x200,  		// размер области пользовательского ППЗУ в байтах
				REVISIONS_QUANTITY_E2010 = INVALID_REVISION_E2010,				// кол-во ревизий модуля
				MODIFICATIONS_QUANTITY_E2010 = INVALID_MODIFICATION_E2010,	// кол-во вариантов исполнения (модификаций) модуля
				ADC_PLUS_OVERLOAD_MARKER_E2010 = 0x5FFF,	// признак 'плюс' перегрузки отсчёта с АЦП (только для Rev.A)
				ADC_MINUS_OVERLOAD_MARKER_E2010 = 0xA000	// признак 'минус' перегрузки отсчёта с АЦП (только для Rev.A)
			};

	// диапазоны входного напряжения АЦП в В
	const double ADC_INPUT_RANGES_E2010[ADC_INPUT_RANGES_QUANTITY_E2010] =
	{
		3.0, 1.0, 0.3
	};
	// диапазон выходного напряжения ЦАП в В
	const double DAC_OUTPUT_RANGE_E2010 = 5.0;
	// доступные ревизии модуля
	const BYTE REVISIONS_E2010[REVISIONS_QUANTITY_E2010] = { 'A', 'B' };
	// доступные исполнения модуля
	const char * const MODIFICATIONS_E2010[MODIFICATIONS_QUANTITY_E2010] = { "BASE", "F5" };

	#pragma pack(1)
	// структура с общей информацией об модуле E20-10
	struct MODULE_DESCRIPTION_E2010
	{
		MODULE_INFO_LUSBAPI     Module;		// общая информация о модуле
		INTERFACE_INFO_LUSBAPI  Interface;	// информация об интерфейсе
		MCU_INFO_LUSBAPI<MCU_VERSION_INFO_LUSBAPI>	Mcu;	// информация о микроконтроллере
		PLD_INFO_LUSBAPI        Pld;			// информация о ПЛИС
		ADC_INFO_LUSBAPI        Adc;			// информация о АЦП
		DAC_INFO_LUSBAPI        Dac;			// информация о ЦАП
		DIGITAL_IO_INFO_LUSBAPI DigitalIo;	// информация о цифровом вводе-выводе
	};
	// структура пользовательского ППЗУ
	struct USER_FLASH_E2010
	{
		BYTE Buffer[USER_FLASH_SIZE_E2010];
	};
	// структура с параметрами синхронизации ввода данных с АЦП
	struct SYNCHRO_PARS_E2010
	{
		WORD	StartSource;				  	// тип и источник сигнала начала сбора данных с АЦП (внутренний или внешний и т.д.)
		DWORD StartDelay; 					// задержка старта сбора данных в кадрах отсчётов c АЦП (для Rev.B и выше)
		WORD	SynhroSource;					// источник тактовых импульсов запуска АЦП (внутренние или внешние и т.д.)
		DWORD StopAfterNKadrs;				// останов сбора данных после задаваемого здесь кол-ва собранных кадров отсчётов АЦП (для Rev.B и выше)
		WORD	SynchroAdMode;   				// режим аналоговой сихронизации: переход или уровень (для Rev.B и выше)
		WORD	SynchroAdChannel;				// физический канал АЦП для аналоговой синхронизации (для Rev.B и выше)
		SHORT SynchroAdPorog;  				// порог срабатывания при аналоговой синхронизации (для Rev.B и выше)
		BYTE	IsBlockDataMarkerEnabled;	// маркирование начала блока данных (удобно, например, при аналоговой синхронизации ввода по уровню) (для Rev.B и выше)
	};
	// структура с параметрами работы АЦП
	struct ADC_PARS_E2010
	{
		BOOL IsAdcCorrectionEnabled;		// управление разрешением автоматической корректировкой получаемых данных на уровне модуля (для Rev.B и выше)
		WORD OverloadMode;					// режим фиксации факта перегрузки входных каналов модуля (только для Rev.A)
		WORD InputCurrentControl;			// управление входным током смещения (для Rev.B и выше)
		SYNCHRO_PARS_E2010 SynchroPars;	// параметры синхронизации ввода данных с АЦП
		WORD ChannelsQuantity;				// кол-во активных каналов (размер кадра отсчётов)
		WORD ControlTable[MAX_CONTROL_TABLE_LENGTH_E2010];	// управляющая таблица с активными логическими каналами
		WORD InputRange[ADC_CHANNELS_QUANTITY_E2010]; 	// индексы диапазонов входного напряжения физических каналов: 3.0В, 1.0В или 0.3В
		WORD InputSwitch[ADC_CHANNELS_QUANTITY_E2010];	// индексы типа подключения физических каналов: земля или сигнал
		double AdcRate;						// частота работы АЦП в кГц
		double InterKadrDelay;				// межкадровая задержка в мс
		double KadrRate;						// частота кадра в кГц
		double AdcOffsetCoefs[ADC_INPUT_RANGES_QUANTITY_E2010][ADC_CHANNELS_QUANTITY_E2010];	// массив коэффициентов для корректировки смещение отсчётов АЦП: (3 диапазона)*(4 канала) (для Rev.B и выше)
		double AdcScaleCoefs[ADC_INPUT_RANGES_QUANTITY_E2010][ADC_CHANNELS_QUANTITY_E2010];		// массив коэффициентов для корректировки масштаба отсчётов АЦП: (3 диапазона)*(4 канала) (для Rev.B и выше)
	};
	// структура с информацией о текущем состоянии процесса сбора данных
	struct DATA_STATE_E2010
	{
		BYTE ChannelsOverFlow;			// битовые признаки перегрузки входных аналоговых каналов (для Rev.B и выше)
		BYTE BufferOverrun;				// битовые признаки переполнения внутреннего буфера модуля
		DWORD CurBufferFilling;			// заполненность внутреннего буфера модуля Rev.B и выше, в отсчётах
		DWORD MaxOfBufferFilling;		// за время сбора максимальная заполненность внутреннего буфера модуля Rev.B и выше, в отсчётах
		DWORD BufferSize;					// размер внутреннего буфера модуля Rev.B и выше, в отсчётах
		double CurBufferFillingPercent;		// текущая степень заполнения внутреннего буфера модуля Rev.B и выше, в %
		double MaxOfBufferFillingPercent;	// за время сбора максимальная степень заполнения внутреннего буфера модуля Rev.B и выше, в %
	};
	#pragma pack()

	//-----------------------------------------------------------------------------
	// интерфейс модуля E20-10
	//-----------------------------------------------------------------------------
	struct ILE2010 : public ILUSBBASE
	{
		// загрузка ПЛИС модуля
		virtual BOOL WINAPI LOAD_MODULE(PCHAR const FileName = NULL) = 0;
		virtual BOOL WINAPI TEST_MODULE(WORD TestModeMask = 0x0) = 0;

		// работа с АЦП
		virtual BOOL WINAPI GET_ADC_PARS(ADC_PARS_E2010 * const AdcPars) = 0;
		virtual BOOL WINAPI SET_ADC_PARS(ADC_PARS_E2010 * const AdcPars) = 0;
		virtual BOOL WINAPI START_ADC(void) = 0;
		virtual BOOL WINAPI STOP_ADC(void) = 0;
		virtual BOOL WINAPI GET_DATA_STATE(DATA_STATE_E2010 * const DataState) = 0;
		virtual BOOL WINAPI ReadData(IO_REQUEST_LUSBAPI * const ReadRequest) = 0;

		// однократная синхронная работа с ЦАП
		virtual BOOL WINAPI DAC_SAMPLE(SHORT * const DacData, WORD DacChannel) = 0;

		// работа с цифровыми линиями
		virtual BOOL WINAPI ENABLE_TTL_OUT(BOOL EnableTtlOut) = 0;
		virtual BOOL WINAPI TTL_IN (WORD * const TtlIn) = 0;
		virtual BOOL WINAPI TTL_OUT(WORD TtlOut) = 0;

		// функции для работы с пользовательской информацией ППЗУ
		virtual BOOL WINAPI ENABLE_FLASH_WRITE(BOOL IsUserFlashWriteEnabled) = 0;
		virtual BOOL WINAPI READ_FLASH_ARRAY(USER_FLASH_E2010 * const UserFlash) = 0;
		virtual BOOL WINAPI WRITE_FLASH_ARRAY(USER_FLASH_E2010 * const UserFlash) = 0;

		// информация о модуле
		virtual BOOL WINAPI GET_MODULE_DESCRIPTION(MODULE_DESCRIPTION_E2010 * const ModuleDescription) = 0;
		virtual BOOL WINAPI SAVE_MODULE_DESCRIPTION(MODULE_DESCRIPTION_E2010 * const ModuleDescription) = 0;
	};

#endif
