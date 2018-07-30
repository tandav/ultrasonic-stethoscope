#include "due_sam3x.init.h"

int main(void)
{
  /* The general init (clock, libc, watchdog disable) */
  init_controller();

  PIO_Configure(PIOB, PIO_OUTPUT_1, PIO_PB27, PIO_DEFAULT);

  while(1)
  {
    PIOB->PIO_SODR = PIO_PB27;
    Sleep(1000);
    PIOB->PIO_SODR = PIO_PB27;
    Sleep(1000);
  }
}
