#include <DueTimer.h>
#include <SineWaveDue.h>


#undef HID_ENABLED
volatile int bufn, obufn;
uint16_t buf[4][256];   // 4 buffers of 256 readings

volatile uint32_t timings[128];



float freq = 1498; // Hz

// times measured in microseconds
// 1 ms ==     1,000 microseconds
// 1  s == 1,000,000 microseconds


const unsigned long tone_duration          =   20000;//
const unsigned long series_duration        = 1000000;//
const unsigned long short_silence_duration =   80000;//
const unsigned long long_silence_duration  = 2000000;//

unsigned long series_start_t        = 0;//
unsigned long short_silence_start_t = 0;
unsigned long long_silence_start_t  = 0;
unsigned long tone_start_t          = 0;

unsigned long chunk_stop            = 0;
byte* chunk_stop_p;
// states:
// 0: play  tone
// 1: short silence
// 2: long  silence
byte state = 0;

boolean series_going = true;
boolean tone_plying  = true;

boolean timing_data_ready = false;


const float pi = 3.14159265;
const float A = 490;                   // amplitude of sine signal
float _T = 50 / 1000000.0;             // set default sampling time in microseconds
float c1;                              // c1 = first filter coefficient, c1b used for second tone
volatile float a[3];                   // filter register for generating tone, updated from interrupt so must be volatile
float omega = 2.0 * pi * freq;         // angular frequency in radians/second
float wTsq = _T * _T * omega * omega ; // omega * sampling frequency squared




void ADC_Handler() {    // move DMA pointers to next buffer
    int f = ADC->ADC_ISR;
    if (f & (1 << 27)) {
        bufn = (bufn + 1) & 3;
        ADC->ADC_RNPR = (uint32_t)buf[bufn];
        ADC->ADC_RNCR = 256;
    }
}

void firstHandler() {
    if (series_going) {
        if (micros() - series_start_t > series_duration) {
            // stop series, start long silence
            series_going = false;
            long_silence_start_t = micros();
            timings[1] = series_start_t;
            timings[2] = series_duration;
            timings[3] = tone_duration;
            timings[4] = short_silence_duration;
            timings[5] = long_silence_duration;
            timing_data_ready = true;
        }
        else { // handling series of tones
            if (tone_plying) {
                if (micros() - tone_start_t < tone_duration) {
                    // play tone samples
                    digitalWrite(LED_BUILTIN, HIGH);
                    a[2] = c1 * a[1] - a[0];     // compute the sample
                    a[0] =      a[1];            // shift the registers in preparation for the next cycle
                    a[1] =      a[2];
                    analogWrite(DAC0, a[2] + 500); // write to DAC
                }
                else {
                    tone_plying = false;
                    short_silence_start_t = micros();
                }
            }
            else {
                if (micros() - short_silence_start_t < short_silence_duration) {
                    digitalWrite(LED_BUILTIN, LOW);
                    analogWrite(DAC0, 0);
                }
                else {
                    tone_plying = true;
                    tone_start_t = micros();
                }
            }        
        }
    }
    else {
        if (micros() - long_silence_start_t < long_silence_duration) {
            digitalWrite(LED_BUILTIN, LOW);
            analogWrite(DAC0, 0);
        }
        else {
            series_going = true;
            series_start_t = micros();
            tone_start_t   = micros();
        }
    }    
}


void setup() {
    timings[0] = 1234567890; // kinda header

    c1   = (8.0 - 2.0 * wTsq) / (4.0 + wTsq); // coefficient of first filter term
    a[0] = 0.0;                               // initialize filter coefficients
    a[1] = A * sin(omega * _T);
    a[2] = 0.0;
    analogReadResolution(10);
    analogWriteResolution(10);
    pinMode(LED_BUILTIN, OUTPUT);
    Timer7.attachInterrupt(firstHandler).start(_T * 1000000);


    SerialUSB.begin(0);
    while (!SerialUSB);
    pmc_enable_periph_clk(ID_ADC);
    adc_init(ADC, SystemCoreClock, ADC_FREQ_MAX, ADC_STARTUP_FAST);
    ADC->ADC_MR |= 0x80; // free running

    ADC->ADC_CHER = 0x80;

    NVIC_EnableIRQ(ADC_IRQn);
    ADC->ADC_IDR = ~(1 << 27);
    ADC->ADC_IER = 1 << 27;
    ADC->ADC_RPR = (uint32_t)buf[0]; // DMA buffer
    ADC->ADC_RCR = 256;
    ADC->ADC_RNPR = (uint32_t)buf[1]; // next DMA buffer
    ADC->ADC_RNCR = 256;
    bufn = obufn = 1;
    ADC->ADC_PTCR = 1;
    ADC->ADC_CR = 2;
}

void loop() {
    if (timing_data_ready) {
        SerialUSB.write((uint8_t *) timings, 512); // 512 bytes = 128 uint32_t (unsigned long == uint32_t on arduino)
        timing_data_ready = false;
    }
    while (obufn == bufn); // wait for buffer to be full
    SerialUSB.write((uint8_t *) buf[obufn], 512); // send it - 512 bytes = 256 uint16_t
    obufn = (obufn + 1) & 3;
    
    chunk_stop = micros();
    chunk_stop_p = (byte*) &chunk_stop;
    SerialUSB.write(chunk_stop_p, 4);
}
