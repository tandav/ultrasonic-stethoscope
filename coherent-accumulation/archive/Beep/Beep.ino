#include <DueTimer.h>
#include <SineWaveDue.h>

float freq = 1000; // Hz


unsigned long t_start;
unsigned long t_stop;

void setup() {
  analogReadResolution(10);
  analogWriteResolution(10);
  Serial.begin(9600);
}

void loop() {
  t_start = millis();

  for (int i = 0; i < 10; i++) {
    sw.playTone(freq, 40);
    delay(5);
  }

  t_stop = millis();

 
  
  Serial.print(t_start);
  Serial.print(' ');
  Serial.print(t_stop);
  Serial.print('\n');
  
  delay(1000);

 
}
