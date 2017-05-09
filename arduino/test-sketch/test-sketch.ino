int analogPin = 0;     // potentiometer wiper (middle terminal) connected to analog pin
                       // outside leads to ground and +5V
int val = 0;           // variable to store the value read

void setup()
{
  Serial.begin(250000);          //  setup serial
}

void loop()
{
  for (int j = 0; j < 360; j++) 
  {
   Serial.println( abs(sin(j * (PI / 180))) );
   Serial.println(0);
  }
}
