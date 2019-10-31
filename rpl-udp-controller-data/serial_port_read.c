 #include "contiki.h"
 #include "dev/serial-line.h"
 #include <stdio.h>

#define UART_BUFFER_SIZE      100 
static uint8_t uart_buffer[UART_BUFFER_SIZE];
static uint8_t uart_buffer_index = 0;

 PROCESS(test_serial, "Serial line test process");
 AUTOSTART_PROCESSES(&test_serial);
 
 
static int serial_input_byte(unsigned char c)
{
   //printf("got input byte: %d ('%c')\n", c, c);
  
   if(c != '\n' && uart_buffer_index < UART_BUFFER_SIZE){
      uart_buffer[uart_buffer_index++] = c;
   }
   else{
      //if(c == '}') uart_buffer[uart_buffer_index++] = c; // JSON specific
      uart_buffer[uart_buffer_index] = '\0';
      uart_buffer_index = 0;
      PRINTF("Received from UART (controller): %s\n",uart_buffer); 
   } 
}


 PROCESS_THREAD(test_serial, ev, data)
 {
 
 	uart1_set_input(serial_input_byte); //just this is enough
 	
   PROCESS_BEGIN();
 
   for(;;) {
     PROCESS_YIELD();
     if(ev == serial_line_event_message) {
       printf("received line: %s\n", (char *)data);
     }
   }
   PROCESS_END();
 }
