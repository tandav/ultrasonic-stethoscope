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


const uint32_t tone_duration          =   1000000/16;
const uint32_t short_silence_duration =   1000000/16;

uint32_t short_silence_start_t = 0;
uint32_t tone_start_t          = 0;

uint32_t tone_playing    =  1; // not shure is it right 
uint32_t current_tone_i  =  0;

boolean timing_data_ready = false;

const float pi = 3.14159265;
const float A = 490;                   // amplitude of sine signal
float _T = 50 / 1000000.0;             // set default sampling time in microseconds
float c1;                              // c1 = first filter coefficient, c1b used for second tone
volatile float a[3];                   // filter register for generating tone, updated from interrupt so must be volatile
float omega = 2.0 * pi * freq;         // angular frequency in radians/second
float wTsq = _T * _T * omega * omega ; // omega * sampling frequency squared


void ADC_Handler() {    // move DMA pointers to next buffer
    int f = ADC -> ADC_ISR;
    if (f & (1 << 27)) {
        bufn = (bufn + 1) & 3;
        ADC -> ADC_RNPR = (uint32_t)buf[bufn];
        ADC -> ADC_RNCR = 256;
    }
}

void firstHandler() {
    if (tone_playing) {
        if (micros() - tone_start_t < tone_duration) {
            // play tone samples (src: https://github.com/cmasenas/SineWaveDue)
            digitalWrite(LED_BUILTIN, HIGH);
            a[2] = c1 * a[1] - a[0];       // compute the sample
            a[0] =      a[1]       ;       // shift the registers in preparation for the next cycle
            a[1] =      a[2]       ;
            analogWrite(DAC0, a[2] + 500); // write to DAC
        }
        else {
            tone_playing = 0;
            timings[1] = tone_playing;

            // reset sine phase
            a[0] = 0.0;
            a[1] = A * sin(omega * _T);
            a[2] = 0.0;
            
            short_silence_start_t = micros();
            timing_data_ready = true;
        }
    }
    else {
        if (micros() - short_silence_start_t < short_silence_duration) {
            digitalWrite(LED_BUILTIN, LOW);
            analogWrite(DAC0, 0);
        }
        else {
            tone_playing = 1;
            current_tone_i += 1;
            timings[1] = tone_playing;
            timings[2] = current_tone_i;
            tone_start_t = micros();
            timing_data_ready = true;
        }
    }        
}    



void setup() {
    for (int i = 0; i < 128; i++)
        timings[i] = 7;
    timings[0] = 1234567890; // kinda header
    timings[1] = tone_playing;
    timings[2] = current_tone_i;
  
    c1   = (8.0 - 2.0 * wTsq) / (4.0 + wTsq); // coefficient of first filter term
    a[0] = 0.0;                               // initialize filter coefficients
    a[1] = A * sin(omega * _T);
    a[2] = 0.0;
    analogWriteResolution(10);
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(DAC0, OUTPUT);
    Timer7.attachInterrupt(firstHandler).start(_T * 1000000);


    SerialUSB.begin(0);
    while (!SerialUSB);
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

void loop() {
    if (timing_data_ready) {
        SerialUSB.write((uint8_t *) timings, 512); // 512 bytes = 128 uint32_t (unsigned long == uint32_t on arduino)
        timing_data_ready = false;
//        current_tone_i = 0;
    }
    while (obufn == bufn); // wait for buffer to be full
    SerialUSB.write((uint8_t *) buf[obufn], 512); // send it - 512 bytes = 256 uint16_t
    obufn = (obufn + 1) & 3;
}
