#include <DueTimer.h>

const float pi = 3.14159 ;
const float A = 490 ;     // amplitude of sine signal

float _T = 50 / 1000000.0 ;       // set default sampling time in microseconds
float c1, c1b, c0;       // c1 = first filter coefficient, c1b used for second tone
volatile float a[3], b[3] ; // filter registers for generating two tones, updated from interrupt so must be volatile


//void compute() {
//  a[2] = c1 * a[1] - a[0];       // compute the sample
//  a[0] = a[1];                   // shift the registers in preparation for the next cycle
//  a[1] = a[2];
//}

//void dac_write() {
//  analogWrite(DAC0, a[2] + 500); // write to DAC
////  delay(1000);
//  Serial.println("228");
//}


//void setup() {

//  Timer1.attachInterrupt(compute);
//  Timer1.start(_T * 1000000);
//  
//  Timer2.attachInterrupt(dac_write);
//  Serial.begin(9600);
//}
//
//void loop() {
//  Serial.println("Beep...!");
//  Timer2.start(_T * 1000000);
//  delay(1000);
//  Timer2.stop();
//  delay(1000);
//}


void dac_write() {
  Serial.println("[-  ] First Handler!");
  a[2] = c1 * a[1] - a[0]; // compute the sample
  a[0] = a[1];             // shift the registers in preparation for the next cycle
  a[1] = a[2];
}

void secondHandler(){
  Serial.println("[ - ] Second Handler!");
}

void thirdHandler(){
  Serial.println("[  -] Third Handler!");
}

void setup() {
  
  float freq = 1000; // Hz
  float omega = 2.0 * pi * freq ;   // angular frequency in radians/second
  float wTsq = _T * _T * omega * omega ; // omega * sampling frequency squared
  c1 = (8.0 - 2.0 * wTsq) / (4.0 + wTsq); // coefficient of first filter term
  a[0] = 0.0;                      // initialize filter coefficients
  a[1] = A * sin(omega * _T);
  a[2] = 0.0;

  analogReadResolution(10);
  analogWriteResolution(10);
  
  Serial.begin(9600);

  Timer3.attachInterrupt(dac_write).start(500000); // Every 500ms
  Timer4.attachInterrupt(secondHandler).start(500000); // Every 500ms

}

void loop(){
//  delay(2000);
//  Timer5.start();

//  delay(2000);
//  Timer5.stop();
}
