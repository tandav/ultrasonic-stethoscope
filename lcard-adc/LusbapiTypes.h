//------------------------------------------------------------------------------
#ifndef __LusbapiTypesH__
#define __LusbapiTypesH__
//------------------------------------------------------------------------------

	#include <windows.h>
	//
	#ifndef NAME_LINE_LENGTH_LUSBAPI
		#define NAME_LINE_LENGTH_LUSBAPI 25
	#endif
	#ifndef COMMENT_LINE_LENGTH_LUSBAPI
		#define COMMENT_LINE_LENGTH_LUSBAPI 256
	#endif
	#ifndef ADC_CALIBR_COEFS_QUANTITY_LUSBAPI
		#define ADC_CALIBR_COEFS_QUANTITY_LUSBAPI 128
	#endif
	#ifndef DAC_CALIBR_COEFS_QUANTITY_LUSBAPI
		#define DAC_CALIBR_COEFS_QUANTITY_LUSBAPI 128
	#endif

	// выравнивание структур
	#pragma pack(1)

	// структура с параметрами запроса на ввод/вывод данных
	struct IO_REQUEST_LUSBAPI
	{
		SHORT * Buffer;							// указатель на буфер данных
		DWORD   NumberOfWordsToPass;			// кол-во отсчётов, которые требуется передать
		DWORD   NumberOfWordsPassed;			// реальное кол-во переданных отсчётов
		OVERLAPPED * Overlapped;				// для асинхроннного запроса - указатель на структура типа OVERLAPPED
		DWORD   TimeOut;							// для синхронного запроса - таймаут в мс
	};

	// структура с информацией об последней ошибке выполнения библиотеки
	struct LAST_ERROR_INFO_LUSBAPI
	{
		BYTE	ErrorString[256];					// строка с кратким описанием последней ошибки
		DWORD	ErrorNumber;	  					// номер последней ошибки
	};

	// информация о ПО, работающем в испольнительном устройстве: MCU, DSP, PLD и т.д.
	struct VERSION_INFO_LUSBAPI
	{
		BYTE 	Version[10];					  	// версия ПО для испольнительного устройства
		BYTE 	Date[14];						  	// дата сборки ПО
		BYTE 	Manufacturer[NAME_LINE_LENGTH_LUSBAPI]; 	// производитель ПО
		BYTE 	Author[NAME_LINE_LENGTH_LUSBAPI];		 	// автор ПО
		BYTE	Comment[COMMENT_LINE_LENGTH_LUSBAPI];		// строка комментария
	};

	// информация о ПО MCU, которая включает в себя информацию о прошивках
	// как основной программы, так и загрузчика
	struct MCU_VERSION_INFO_LUSBAPI
	{
		VERSION_INFO_LUSBAPI FwVersion;						// информация о версии прошивки основной программы 'Приложение'(Application) микроконтроллера
		VERSION_INFO_LUSBAPI BlVersion;						// информация о версии прошивки 'Загрузчика'(BootLoader) микроконтроллера
	};

	// общая информация о модуле (штатный вариант)
	struct MODULE_INFO_LUSBAPI
	{
		BYTE	CompanyName[NAME_LINE_LENGTH_LUSBAPI];		// название фирмы-изготовителя изделия
		BYTE	DeviceName[NAME_LINE_LENGTH_LUSBAPI]; 		// название изделия
		BYTE	SerialNumber[16];									// серийный номер изделия
		BYTE	Revision;											// ревизия изделия (латинская литера)
		BYTE	Modification;										// исполнение модуля (число);
		BYTE	Comment[COMMENT_LINE_LENGTH_LUSBAPI];		// строка комментария
	};

	// общая информация о модуле (с дополнительным полем Modification)
/*	struct MODULE_INFO_M_LUSBAPI
	{
		BYTE	CompanyName[NAME_LINE_LENGTH_LUSBAPI];		// название фирмы-изготовителя изделия
		BYTE	DeviceName[NAME_LINE_LENGTH_LUSBAPI]; 		// название изделия
		BYTE	SerialNumber[16];									// серийный номер изделия
		BYTE	Revision;											// ревизия изделия (латинская литера)
		BYTE	Modification;										// исполнение модуля (число);
		BYTE	Comment[COMMENT_LINE_LENGTH_LUSBAPI];		// строка комментария
	};*/

	// информация о DSP
	struct DSP_INFO_LUSBAPI
	{
		BOOL	Active;												// флаг достоверности остальных полей структуры
		BYTE	Name[NAME_LINE_LENGTH_LUSBAPI];				// название DSP
		double	ClockRate;										// тактовая частота работы DSP в кГц
		VERSION_INFO_LUSBAPI Version;							// информация о драйвере DSP
		BYTE	Comment[COMMENT_LINE_LENGTH_LUSBAPI];		// строка комментария
	};

	// информация о микроконтроллере
	template <class VersionType>
	struct MCU_INFO_LUSBAPI
	{
		BOOL	Active;												// флаг достоверности остальных полей структуры
		BYTE	Name[NAME_LINE_LENGTH_LUSBAPI];				// название микроконтроллера
		double	ClockRate;										// тактовая частота работы микроконтроллера в кГц
//		VERSION_INFO_LUSBAPI Version;							// информация о версии прошивки микроконтроллера
		VersionType Version;										// информация о версии как самой прошивки микроконтроллера, так, возможно, и прошивки 'Загрузчика'
		BYTE	Comment[COMMENT_LINE_LENGTH_LUSBAPI];		// строка комментария
	};

	// информация о ПЛИС (PLD)
	struct PLD_INFO_LUSBAPI										// PLD - Programmable Logic Device
	{
		BOOL	Active;												// флаг достоверности остальных полей структуры
		BYTE	Name[NAME_LINE_LENGTH_LUSBAPI];		  		// название ПЛИС
		double ClockRate;											// тактовая чатота работы ПЛИС в кГц
		VERSION_INFO_LUSBAPI Version;							// информация о версии прошивки ПЛИС
		BYTE	Comment[COMMENT_LINE_LENGTH_LUSBAPI];		// строка комментария
	};

	// информация о АЦП
	struct ADC_INFO_LUSBAPI
	{
		BOOL	Active;												// флаг достоверности остальных полей структуры
		BYTE	Name[NAME_LINE_LENGTH_LUSBAPI];				// название микросхемы АЦП
		double	OffsetCalibration[ADC_CALIBR_COEFS_QUANTITY_LUSBAPI];	// корректировочные коэффициенты смещения нуля
		double	ScaleCalibration[ADC_CALIBR_COEFS_QUANTITY_LUSBAPI];		// корректировочные коэффициенты масштаба
		BYTE	Comment[COMMENT_LINE_LENGTH_LUSBAPI];		// строка комментария
	};

	// информация о ЦАП
	struct DAC_INFO_LUSBAPI
	{
		BOOL	Active;												// флаг достоверности остальных полей структуры
		BYTE	Name[NAME_LINE_LENGTH_LUSBAPI];				// название микросхемы ЦАП
		double	OffsetCalibration[DAC_CALIBR_COEFS_QUANTITY_LUSBAPI];	// корректировочные коэффициенты
		double	ScaleCalibration[DAC_CALIBR_COEFS_QUANTITY_LUSBAPI];		// корректировочные коэффициенты
		BYTE	Comment[COMMENT_LINE_LENGTH_LUSBAPI];		// строка комментария
	};

	// информация о цифрового ввода-вывода
	struct DIGITAL_IO_INFO_LUSBAPI
	{
		BOOL	Active;												// флаг достоверности остальных полей структуры
		BYTE	Name[NAME_LINE_LENGTH_LUSBAPI];				// название цифровой микросхемы
		WORD	InLinesQuantity;	 								// кол-во входных линий
		WORD	OutLinesQuantity; 								// кол-во выходных линий
		BYTE	Comment[COMMENT_LINE_LENGTH_LUSBAPI];		// строка комментария
	};

	// информация о используемого интерфейса для доступа к модулю
	struct INTERFACE_INFO_LUSBAPI
	{
		BOOL	Active;												// флаг достоверности остальных полей структуры
		BYTE	Name[NAME_LINE_LENGTH_LUSBAPI];			 	// название
		BYTE	Comment[COMMENT_LINE_LENGTH_LUSBAPI];		// строка комментария
	};
	//
	#pragma pack()

#endif
