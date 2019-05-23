/*
ADC:
Input: Analog in A0
Output: Raw stream of uint16_t in range 0-4095 on Native USB Serial/ACM
*/

#include <Wire.h>
#include <SPI.h>
//#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>
#include <DueTimer.h>


#define BMP_CS 8
#define BMP_MOSI 11 // sdi
#define BMP_MISO 12 // sdo
#define BMP_SCK 13

#define BMP_2_CS 7
#define BMP_2_MOSI 5 // sdi
#define BMP_2_MISO 6 // sdo
#define BMP_2_SCK 4

#define BEEP_PIN DAC1


const int header_length = 4;
const int payload_length = 4 + 4 + 1 + 512; // 2 bmp sensors, is_tone_playing, adc mic
const int packet_length = header_length + payload_length;

uint8_t header[header_length] = { 0xd2, 0x2, 0x96, 0x49 };
uint8_t packet[packet_length];

//typedef union {
//    float   _float;
//    uint8_t bytes[4];
//} union_float;

//union_float b0;
//union_float b1;

float bmp0_prev = 0;
float bmp1_prev = 0;

float bmp0_new;
float bmp1_new;

volatile float bmp_buffer[2];



// times measured in microseconds
// 1 ms ==     1,000 microseconds
// 1  s == 1,000,000 microseconds

float freq = 1498; // Hz

const uint32_t tone_duration          =   1000000/16;
const uint32_t short_silence_duration =   1000000/16;
uint32_t short_silence_start_t = 0;
uint32_t tone_start_t          = 0;

uint8_t is_tone_playing = 1; // maybe its better to start with 0, idk


const float A = 490;                           // amplitude of sine signal
const float pi = 3.14159265;
float _T = 50 / 1000000.0;                     // set default sampling time in microseconds
volatile float a[3];                           // filter register for generating tone, updated from interrupt so must be volatile
float omega = 2.0 * pi * freq;                 // angular frequency in radians/second
float wTsq = _T * _T * omega * omega;          // omega * sampling frequency squared
float c1  = (8.0 - 2.0 * wTsq) / (4.0 + wTsq); // c1 = first filter coefficient, c1b used for second tone


// Adafruit_BMP280 bme; // I2C
// Adafruit_BMP280 bme(BMP_CS); // hardware SPI
// software SPI (my varik)
Adafruit_BMP280 bmp0(BMP_CS, BMP_MOSI, BMP_MISO,  BMP_SCK);
Adafruit_BMP280 bmp1(BMP_2_CS, BMP_2_MOSI, BMP_2_MISO,  BMP_2_SCK);



uint16_t buffer[256];

volatile int bufn, obufn;
uint16_t buf[4][256];   // 4 buffers of 256 readings

float cc = 0;


void ADC_Handler() {    // move DMA pointers to next buffer
    int f = ADC -> ADC_ISR;
    if (f & (1 << 27)) {
        bufn = (bufn + 1) & 3;
        ADC -> ADC_RNPR = (uint32_t)buf[bufn];
        ADC -> ADC_RNCR = 256;
    }
}


void init_adc() {
//    SerialUSB.begin(0); // Initialize Native USB port
//    while (!SerialUSB); // Wait until connection is established

    pmc_enable_periph_clk(ID_ADC);
    adc_init(ADC, SystemCoreClock, ADC_FREQ_MAX, ADC_STARTUP_FAST);
    ADC -> ADC_MR |= 0x80; // free running

    ADC -> ADC_CHER = 0x80;

    NVIC_EnableIRQ(ADC_IRQn);
    ADC -> ADC_IDR = ~(1 << 27);
    ADC -> ADC_IER = 1 << 27;
    ADC -> ADC_RPR = (uint32_t)buf[0]; // DMA buffer
    ADC -> ADC_RCR = 256;
    ADC -> ADC_RNPR = (uint32_t)buf[1]; // next DMA buffer
    ADC -> ADC_RNCR = 256;
    bufn = obufn = 1;
    ADC -> ADC_PTCR = 1;
    ADC -> ADC_CR = 2;
}

void beep_handler() {
    if (is_tone_playing) {
        if (micros() - tone_start_t < tone_duration) {
            // play tone samples (src: https://github.com/cmasenas/SineWaveDue)
            digitalWrite(LED_BUILTIN, HIGH);
            a[2] = c1 * a[1] - a[0];       // compute the sample
            a[0] =      a[1]       ;       // shift the registers in preparation for the next cycle
            a[1] =      a[2]       ;
            analogWrite(BEEP_PIN, a[2] + 500); // write to DAC
        }
        else {
            is_tone_playing = 0;

            // reset sine phase (without reset, phases of sine-tones are constantly shifting)
            a[0] = 0.0;
            a[1] = A * sin(omega * _T);
            a[2] = 0.0;

            short_silence_start_t = micros();
        }
    }
    else {
        if (micros() - short_silence_start_t < short_silence_duration) {
            digitalWrite(LED_BUILTIN, LOW);
            analogWrite(BEEP_PIN, 0);
        }
        else {
            is_tone_playing = 1;
            tone_start_t = micros();
        }
    }
}

void bmp_handler() {
    bmp_buffer[0] = bmp0.readPressure();
    bmp_buffer[1] = bmp1.readPressure();
}

//int min0  = 50;
//int min1  = 10000;
//int max0  = 1000;
//int max1  = 1000000;
//int steps = 10;
//int gp_curr = min1;
//volatile uint32_t gpc[2];
//const uint32_t gpt = 1000000;
//uint32_t gp_start  = 0;
//gpc[0] = min0;
//gpc[1] = min1;


void setup() {

    if (!bmp0.begin()) {
        // SerialUSB.println(F("Could not find a valid BMP280 0 sensor, check wiring!"));
        while (1);
    }

    if (!bmp1.begin()) {
        // SerialUSB.println(F("Could not find a valid BMP280 1 sensor, check wiring!"));
        while (1);
    }

    analogWriteResolution(10);
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(BEEP_PIN, OUTPUT);
    Timer1.attachInterrupt(beep_handler).start(50);
//    Timer1.attachInterrupt(beep_handler).start(100);
//    Timer1.attachInterrupt(beep_handler).start(800);
//    Timer2.attachInterrupt(bmp_handler).start(1250);
    Timer2.attachInterrupt(bmp_handler).start(100000/2);

    SerialUSB.begin(0); // Initialize Native USB port
    while (!SerialUSB); // Wait until connection is established

    init_adc();
}


void loop() {
//
//    if (micros() - gp_start < gpt) {
//        gpc[1] += (max1 - min1) / steps;
//        gp_start = micros();
//        Timer2.setPeriod(gpc[1]);
//    }

    for (int i = 0; i < header_length; i++)
        packet[i] = header[i];


//    bmp_buffer[0] = cc;
//    bmp_buffer[1] = cc + 10;
//
//    cc += 1;
//    if (cc > 128) {
//        cc = 0;
//    }



//    bmp_buffer[0] = 3.1415;
//    bmp_buffer[1] = 2.1213;
//    bmp_buffer[0] = bmp0.readPressure();
//    bmp_buffer[1] = bmp1.readPressure();


    uint8_t* bmp_buffer_bytes = (uint8_t *) bmp_buffer;

    for (int i = 0; i < 8; i++)
        packet[4 + i] = bmp_buffer_bytes[i];



//    b0._float = bmp0.readPressure();
//    b1._float = bmp1.readPressure();

//    b0._float = 3.1415;
//    b1._float = 2.1213;

//    packet[ 4] = b0.bytes[0];
//    packet[ 5] = b0.bytes[1];
//    packet[ 6] = b0.bytes[2];
//    packet[ 7] = b0.bytes[3];
//
//    packet[ 8] = b1.bytes[0];
//    packet[ 9] = b1.bytes[1];
//    packet[10] = b1.bytes[2];
//    packet[11] = b1.bytes[3];

    packet[12] = is_tone_playing;
    //    is_tone_playing = !is_tone_playing;


//    if (is_tone_playing)
//        for (int i = 0; i < 256; i++)
//            buffer[i] = i;
//    else
//        for (int i = 0; i < 256; i++)
//            buffer[i] = 0;
//
//    uint8_t* buffer_bytes = (uint8_t *) buffer;

    while (obufn == bufn); // wait for buffer to be full
    uint8_t* buffer_bytes = (uint8_t *) buf[obufn];
    obufn = (obufn + 1) & 3; // 0 1 2 3 0 1 2 3 0 1 2 3 ..., like % 3

    for (int i = 0; i < 512; i++)
        packet[13 + i] = buffer_bytes[i];


//    uint8_t* gpc_bytes = (uint8_t *) gpc_bytes;
//
//    for (int i = 0; i < 8; i++)
//        packet[525 + i] = gpc_bytes[i];

    SerialUSB.write(packet, packet_length);
}
