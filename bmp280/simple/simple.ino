#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>

#define BMP_SCK 13
#define BMP_MISO 12 // sdo
#define BMP_MOSI 11 // sdi
#define BMP_CS 8

#define BMP_2_SCK 4
#define BMP_2_MISO 6 // sdo
#define BMP_2_MOSI 5 // sdi
#define BMP_2_CS 7


const int bs = 2;

float buffer[bs];

float bmp0_prev = 0;
float bmp1_prev = 0;

float bmp0_new;
float bmp1_new;

//Adafruit_BMP280 bmp; // I2C
//Adafruit_BMP280 bmp(BMP_CS); // hardware SPI
// software SPI (my varik)
Adafruit_BMP280 bmp0(BMP_CS, BMP_MOSI, BMP_MISO,  BMP_SCK);
Adafruit_BMP280 bmp1(BMP_2_CS, BMP_2_MOSI, BMP_2_MISO,  BMP_2_SCK);


  
void setup() {
    // Serial.begin(9600);
    SerialUSB.begin(0);
    while (!SerialUSB);

    // default settings
    // bmp0.setSampling(
    //     Adafruit_BMP280::MODE_NORMAL,   /* Operating Mode. */
    //     Adafruit_BMP280::SAMPLING_X2,   /* Temp. oversampling */
    //     Adafruit_BMP280::SAMPLING_X16,  /* Pressure oversampling */
    //     Adafruit_BMP280::FILTER_OFF,    /* Filtering. */
    //     Adafruit_BMP280::STANDBY_MS_1   /* Standby time. */
    // );

    // bmp1.setSampling(
    //     Adafruit_BMP280::MODE_NORMAL,   /* Operating Mode. */
    //     Adafruit_BMP280::SAMPLING_X2,   /* Temp. oversampling */
    //     Adafruit_BMP280::SAMPLING_X16,  /* Pressure oversampling */
    //     Adafruit_BMP280::FILTER_OFF,    /* Filtering. */
    //     Adafruit_BMP280::STANDBY_MS_1   /* Standby time. */
    // );
  
    if (!bmp0.begin()) {  
        // SerialUSB.println("Could not find a valid BMP280 1 sensor, check wiring!");
        while (1);
    }

    if (!bmp1.begin()) {  
        // SerialUSB.println("Could not find a valid BMP280 2 sensor, check wiring!");
        while (1);
    }



}

  
void loop() {
    bmp0_new = bmp0.readPressure();
    bmp1_new = bmp1.readPressure();

    if (bmp0_new != bmp0_prev || bmp1_new != bmp1_prev) {
        buffer[0] = bmp0_new;
        buffer[1] = bmp1_new;

        bmp0_prev = bmp0_new;
        bmp1_prev = bmp1_new;

        SerialUSB.write((uint8_t *) buffer, bs * sizeof(float));
    }

    // buffer[0] = bmp0.readPressure();
    // buffer[1] = bmp1.readPressure();
    
    // Serial.print(bmp0.readPressure());
    // Serial.print(bmp1.readPressure());

    
    // delay(5);
}
