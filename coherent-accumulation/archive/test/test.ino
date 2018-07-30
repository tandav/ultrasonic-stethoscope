double t;
const double pi = 3.141592653589793238462643;
int val = 0;      // variable to store the value read
double f = 1000;  // sine wave frequency in Hz
double current_t_in_seconds = 0;

int out_pin = 3;

void setup() {

  //  analogWriteResolution(12);  // set the analog output resolution to 12 bit (4096 levels)
  //  analogReadResolution(12);   // set the analog input resolution to 12 bit
  Serial.begin(9600);
  pinMode(out_pin, OUTPUT); // declare pin 9 to be an output:
}


double map_double(double x, double in_min, double in_max, double out_min, double out_max) {
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

void loop() {
  //  analogWrite(DAC0, waveformsTable[wave0][i]);  // write the selected waveform on DAC0
  //  analogWrite(DAC1, waveformsTable[wave1][i]);  // write the selected waveform on DAC1
  //  Serial.println(waveformsTable[wave0][i]);

  t = micros() * 0.000001; // convert microseconds to seconds
  //  Serial.println(t);


  //  val = (int) map_double(sin(2 * pi * f * t), -1, 1, 0, 255);
  val = (int) map_double(sin(2 * pi * f * t), -1, 1, 0, 4095);

  analogWrite(DAC0, val);
  //  analogWrite(out_pin, val);

  Serial.println(val);

}
