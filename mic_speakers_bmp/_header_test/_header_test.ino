const int header_length = 4;
const int payload_length = 541;
const int packet_length = header_length + payload_length;


uint8_t header[header_length] = { 0xd2, 0x2, 0x96, 0x49 };
uint8_t packet[packet_length ];


void setup() {
    SerialUSB.begin(0); // Initialize Native USB port
    while (!SerialUSB); // Wait until connection is established
}


void loop() {

    for (int i = 0; i < header_length; i++)
        packet[i] = header[i];

    for (int i = 0; i < payload_length; i++)
        packet[i + header_length] = i;

    SerialUSB.write(packet, packet_length);
}
