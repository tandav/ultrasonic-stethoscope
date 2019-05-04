#include <Wire.h>
#include <SPI.h>
//#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>

#define BMP_CS 8
#define BMP_MOSI 11 // sdi
#define BMP_MISO 12 // sdo
#define BMP_SCK 13


#define BMP_2_CS 7
#define BMP_2_MOSI 5 // sdi
#define BMP_2_MISO 6 // sdo
#define BMP_2_SCK 4



typedef union { float _float; uint8_t bytes[4]; } union_float;
uint8_t is_tone_playing = true;

// unsigned long == uint32_t on arduino)

//float buffer[2];

uint8_t packet[9];

// Adafruit_BMP280 bme; // I2C
// Adafruit_BMP280 bme(BMP_CS); // hardware SPI
// software SPI (my varik)
Adafruit_BMP280 bmp0(BMP_CS, BMP_MOSI, BMP_MISO,  BMP_SCK);
Adafruit_BMP280 bmp1(BMP_2_CS, BMP_2_MOSI, BMP_2_MISO,  BMP_2_SCK);

//uint32_t n = 0;
//volatile uint32_t timings[128];

void setup() {


//    typedef struct {
//        uint16_t adc_mic[256];
//        bool is_tone_playing;
//        uint32_t bmp0_pressure;
//        uint32_t bmp1_pressure;
//    } packet;

//    typedef union {
//        packet p;
//        uint8_t packet_bytes;
//    } union_packet;



    Serial.begin(9600);
    Serial.println(F("BMP280 test"));

    if (!bmp0.begin()) {
        // SerialUSB.println(F("Could not find a valid BMP280 0 sensor, check wiring!"));
        while (1);
    }

    if (!bmp1.begin()) {
        // SerialUSB.println(F("Could not find a valid BMP280 1 sensor, check wiring!"));
        while (1);
    }

    // maybe rename to just Serial
    SerialUSB.begin(0); // Initialize Native USB port
    while (!SerialUSB); // Wait until connection is established
}

void loop() {

    union_float b0;
    union_float b1;

//    b0._float = 3.14159265;// bmp0.readPressure();
//    b1._float = 2.71828   ;// bmp1.readPressure();

    b0._float = bmp0.readPressure();
    b1._float = bmp1.readPressure();

    is_tone_playing = !is_tone_playing;

    packet[0] = b0.bytes[0];
    packet[1] = b0.bytes[1];
    packet[2] = b0.bytes[2];
    packet[3] = b0.bytes[3];

    packet[4] = b1.bytes[0];
    packet[5] = b1.bytes[1];
    packet[6] = b1.bytes[2];
    packet[7] = b1.bytes[3];

    packet[8] = is_tone_playing;


    //    uint8_t packet[8]

    //    buffer[0] = bmp0.readPressure();
    //    buffer[1] = bmp1.readPressure();

    SerialUSB.write(packet, 8);
    //    delay(5);

    //    uint32_t x[2];

    //    x[0] = 0;
    //    x[1] = 1;x

    //    SerialUSB.write(x, 8); // error


    //    SerialUSB.write((byte     *) x, 8); // ok
    //    SerialUSB.write((char     *) x, 8); // ok
    //    SerialUSB.write((uint8_t  *) x, 8); // ok
    //    SerialUSB.write((uint32_t *) x, 2); // error


    //    uint32_t y[2];
    //
    //    y[0] = 2;
    //    y[1] = 3;
    //
    //    SerialUSB.write((byte *) x, 8);
    //    SerialUSB.write((byte *) y, 8);
    //
    //    SerialUSB.write((uint32_t *) x, 2);
    //    SerialUSB.write((uint32_t *) y, 2);


    //    for (int i = 0; i < 128; i++)
    //        timings[i] = i;

    //    uint32_t timings[128];

    // 128 uint32_t == 512 bytes
    //    SerialUSB.write((byte *) timings, 512);



    // (char *) == (byte *)



    //    SerialUSB.write((uint8_t *) timings, 512); // 512 bytes = 128 uint32_t (unsigned long == uint32_t on arduino)
    //    SerialUSB.write(&timings, 512); // 512 bytes = 128 uint32_t (unsigned long == uint32_t on arduino)

    //    Serial.print("Value = ");
        //  Serial.print(n);
    //    n += 1;
    //    delay(2000);
}
