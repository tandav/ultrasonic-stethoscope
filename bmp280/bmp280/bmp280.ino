/***************************************************************************
  This is a library for the BMP280 humidity, temperature & pressure sensor

  Designed specifically to work with the Adafruit BMEP280 Breakout 
  ----> http://www.adafruit.com/products/2651

  These sensors use I2C or SPI to communicate, 2 or 4 pins are required 
  to interface.

  Adafruit invests time and resources providing this open source code,
  please support Adafruit andopen-source hardware by purchasing products
  from Adafruit!

  Written by Limor Fried & Kevin Townsend for Adafruit Industries.  
  BSD license, all text above must be included in any redistribution
 ***************************************************************************/

#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>

#define BMP_SCK 13
#define BMP_MISO 12 // sdo
#define BMP_MOSI 11 // sdi
#define BMP_CS 10

#define BMP_2_SCK 4
#define BMP_2_MISO 6 // sdo
#define BMP_2_MOSI 5 // sdi
#define BMP_2_CS 7

//Adafruit_BMP280 bme; // I2C
//Adafruit_BMP280 bme(BMP_CS); // hardware SPI
// software SPI (my varik)
Adafruit_BMP280 bme1(BMP_CS, BMP_MOSI, BMP_MISO,  BMP_SCK);
Adafruit_BMP280 bme2(BMP_2_CS, BMP_2_MOSI, BMP_2_MISO,  BMP_2_SCK);
  
void setup() {
  Serial.begin(9600);
  Serial.println(F("BMP280 test"));
  
  if (!bme1.begin()) {
    Serial.println("Could not find a valid BMP280 1 sensor, check wiring!");
    while (1);
  }

  if (!bme2.begin()) {
    Serial.println("Could not find a valid BMP280 2 sensor, check wiring!");
    while (1);
  }
}
  
void loop() {
    // Sensor 1
    Serial.println("S E N S O R   1");
    Serial.print("Temperature = ");
    Serial.print(bme1.readTemperature());
    Serial.println(" *C");
    
    Serial.print("Pressure = ");
    Serial.print(bme1.readPressure());
    Serial.println(" Pa");

    Serial.print("Approx altitude = ");
    Serial.print(bme1.readAltitude(1013.25)); // this should be adjusted to your local forcase
    Serial.println(" m");

    Serial.println();
    
    //Sensor 2
    Serial.println("S E N S O R    2");
    Serial.print("Temperature = ");
    Serial.print(bme2.readTemperature());
    Serial.println(" *C");
    
    Serial.print("Pressure = ");
    Serial.print(bme2.readPressure());
    Serial.println(" Pa");

    Serial.print("Approx altitude = ");
    Serial.print(bme2.readAltitude(1013.25)); // this should be adjusted to your local forcase
    Serial.println(" m");
    
    Serial.println();
    delay(2000);
}
