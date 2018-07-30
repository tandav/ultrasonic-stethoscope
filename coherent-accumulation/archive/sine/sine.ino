int pwm_pin    = 9;      // the PWM pin the LED is attached to
int analogPin  = 3;
int value      = 0;
float f        = 10;  // sine wave frequency
unsigned long t;
const float pi = 3.141592653589793238462643;
int val        = 0;      // variable to store the value read
unsigned long T = 10;
unsigned long t0;

unsigned long start_t;
unsigned long   end_t;
//bool

void setup() {              // the setup routine runs once when you press reset:
  pinMode(pwm_pin, OUTPUT); // declare pin 9 to be an output:
  Serial.begin(9600);
}

// the loop routine runs over and over again forever:

void loop() {
  //  start_t = micros();
  //  while (micros() < 4000000) {
  //  start_t = micros();

  t0 = micros();
  t  = micros();

  while (t - t0 < T) {
    t = micros();
    analogWrite(pwm_pin, value); // allowed range is [0..255]
    Serial.println(value);
  }

  if (value == 0) value = 255;
  else value = 0;
    //  Serial.println(micros() - start_t);
    //  }
    //  Serial.println(micros());
    //  Serial.println(micros() - start_t);
    //    t =
    //    t = micros();

    //  value = 255 / 2 * (sin(2 * pi * f * t) + 1);
    //    value = map(sin(2 * pi * f * t), -1, 1, 0, 255); // works wrong, read more about map
    //    value = map(sin(f * t), -1.0, 1.0, 0.0, 255.0);
    //  value = sin(f * t);

    //  T = 1000;
    //  Serial.println(sin(f * t));
    //  Serial.println(value);
    //  analogWrite(pwm_pin, value); // allowed range is [0..255]


    //  if (t - t0 > T) {
    //    value = 255;
    //    t0 = t;
    //  }
    //  else {
    //
    //  }
    //  if (value == 0) value = 255;
    //  else value = 0;
    //  value = 0 ? 255 : 0;
    //  Serial.println(t);
    //  analogWrite(pwm_pin, value); // allowed range is [0..255]

    //  val = analogRead(analogPin);     // read the input pin
    //  Serial.println(val);

    //  Serial.print(sin(f * t));
    //  Serial.print('\t');
    //  Serial.print(map(sin(f * t), -1, 1, -2, 2));
    //  Serial.print('\n');
    //    delay(10); // milliseconds
  }

