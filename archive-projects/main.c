#include <stdio.h>
#include <stdint.h>

// clang main.c && ./a.out

int main(void) {

//    union {
//        uint16_t uint16[256];
//        uint8_t  uint8 [512];
//    } buffer;


    uint8_t header[4] = { 0xd2, 0x2, 0x96, 0x49 };


    printf("%u\n", header[0]);
    printf("%u\n", header[1]);
    printf("%u\n", header[2]);
    printf("%u\n", header[3]);

    // uint16_t buffer[256];

//    for (int i = 0; i < 256; i++)
//        buffer.uint16[i] = i;

//    for (int i = 0; i < 256; i++)
//        printf("%u\t%u\n", buffer.uint16[i], buffer.uint8[i]);

    // uint8_t* buffer_bytes = (uint8_t *) buffer;

//    for (int i = 0; i < 256; i++)
        // printf("%u\t%u\n", buffer[i], buffer_bytes[i]);
    // if (buffer[0] == buffer_bytes[0])
        // printf("true\n");
    // else
        // printf("false\n");
    // printf("%s", x ? "true" : "false");
    // printf("Hello%zu\n", sizeof(buffer_bytes));
    return 0;
}
