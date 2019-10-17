#include "contiki.h"
#include "contiki-lib.h"
#include "contiki-net.h"
#include "net/ip/uip.h"
#include "net/rpl/rpl.h"

#include "net/netstack.h"
#include "dev/button-sensor.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

//#define DEBUG DEBUG_PRINT
#include "net/ip/uip-debug.h"

/**** Read from serial port  ******/
 #include "dev/serial-line.h"
#define UART_BUFFER_SIZE      100 
static uint8_t uart_buffer[UART_BUFFER_SIZE];
static uint8_t uart_buffer_index = 0;
/*********************************/

#ifndef PERIOD
#define PERIOD 60 // if it is short, INCREASE IT.
#endif

#define START_INTERVAL		(15 * CLOCK_SECOND)
#define SEND_INTERVAL		(PERIOD * CLOCK_SECOND)
#define SEND_TIME		(random_rand() % (SEND_INTERVAL))

#define UIP_IP_BUF   ((struct uip_ip_hdr *)&uip_buf[UIP_LLH_LEN])

#define UDP_CLIENT_PORT	8765
#define UDP_SERVER_PORT	5678

#define UDP_EXAMPLE_ID  190

static struct uip_udp_conn *server_conn;
static rpl_dag_t *dag; //global
int counter; //counting rounds. Not really needed

PROCESS(udp_server_process, "UDP server process");
AUTOSTART_PROCESSES(&udp_server_process);
/*---------------------------------------------------------------------------*/
static void
tcpip_handler(void)
{
  char *appdata;
  uip_ipaddr_t *child_node; 

  if(uip_newdata()) {
    appdata = (char *)uip_appdata;
    appdata[uip_datalen()] = 0;
    PRINTF("DATA recv '%s' from ", appdata);
    PRINTF("%d",UIP_IP_BUF->srcipaddr.u8[sizeof(UIP_IP_BUF->srcipaddr.u8) - 1]);
    PRINTF("\n");
    
    /* node is sending a New Parent */
    if(appdata[1] == 'N' && appdata[2] == 'P'){
			child_node = &UIP_IP_BUF->srcipaddr;
		   /* Need to convert again the sourceIP from global to local
			 * i.e., from fd00 --. fe00. We dont want to play 
			 * with the protocol, hence, return a local variable.
			 */ 				
		   child_node->u8[0] = (uint8_t *)254;
		   child_node->u8[1] = (uint8_t *)128;    
    		
    		/* conntroller reads line starting with 2 chars (NP, etc.) */
			printf("%s from ", appdata);
			printLongAddr(child_node);	
			printf("\n");     
    }
    
#if SERVER_REPLY
    PRINTF("DATA sending reply\n");
    uip_ipaddr_copy(&server_conn->ripaddr, &UIP_IP_BUF->srcipaddr);
    uip_udp_packet_send(server_conn, "Reply", sizeof("Reply"));
    uip_create_unspecified(&server_conn->ripaddr);
#endif
  }
}
/*---------------------------------------------------------------------------*/
/****************NOT USED! Direct children, only once *******************/
static void 
print_all_neighbors(void)
{
	/*
	 * The same information (sink's direct children),
	 * can be aquired from the routes. When child = father,
	 * this is a direct child of sink.
	 */	 
	uip_ds6_nbr_t *nbr = nbr_table_head(ds6_neighbors);
	//printf("Counter %d: My nbr-children only: \n",counter);    	
	
	while(nbr != NULL) {
		printf("Sinks child: ");
		printLongAddr(&nbr->ipaddr);
		printf("\n");
		nbr = nbr_table_next(ds6_neighbors, nbr);
	}
	//printf("End of neighbors\n"); 		
}
/*-------------- All direct children and their descentants -------------------*/
static void
print_all_routes(void)
{
	uip_ds6_route_t *r;
	uip_ipaddr_t *nexthop;
	uip_ipaddr_t *local_child; 
		 	 	
	for(r = uip_ds6_route_head();
		r != NULL;
		r = uip_ds6_route_next(r)) {
		
		 nexthop = uip_ds6_route_nexthop(r);
		  
		 local_child = &r->ipaddr;

		 PRINTF("Counter: %d Route: %02d -> %02d", counter, 
					r->ipaddr.u8[15], nexthop->u8[15]);

		/* BE CAREFUL: WE DONT WANT TO MESS WITH THE IPs in RPL.
		 * Hence local_child will be transformed from global IP to
		 * local IP, by transforming local_child[0] from fd00 to fe80
		 */		 
		 local_child->u8[0] = (uint8_t *)254;
		 local_child->u8[1] = (uint8_t *)128;
		 
		 /* Controller is reading a line starting from "Route " */
		 printf("Route: ");
		 printLongAddr(local_child); //direct child
		 // printLongAddr(&r->ipaddr); // fd00:...
		 printf(" ");
		 printLongAddr(nexthop); // all decentant(s)
		 /* when lt->0, the connection does not exist any more */
		 printf(" lt:%lu\n", r->state.lifetime);	 
	}//for *r 
} 	
/*---------------------------------------------------------------------------*/
static void
print_stats(void)
{
#define PRINTROUTES 1
#define PRINTNBRS 0

	printf("Printing all ENABLED stats\n");  
		 
#if PRINTROUTES  
	print_all_routes();
#endif	 

#if PRINTNBRS
	print_all_neighbors(); // it seems to have problems. NOT to be USED ???
#endif

	if(counter % 10   == 0){ // just print this info every modulo % rounds...
		printf("I am sink: "); 
		/* fd00 NOT fe80 */
		printLongAddr(&dag->dag_id);  
		printf("\n");
	}
}
/*---------------------------------------------------------------------------*/
static void
print_local_addresses(void)
{
  int i;
  uint8_t state;

  PRINTF("Server IPv6 addresses: ");
  for(i = 0; i < UIP_DS6_ADDR_NB; i++) {
    state = uip_ds6_if.addr_list[i].state;
    if(state == ADDR_TENTATIVE || state == ADDR_PREFERRED) {
      PRINT6ADDR(&uip_ds6_if.addr_list[i].ipaddr);
      PRINTF("\n");
      /* hack to make address "final" */
      if (state == ADDR_TENTATIVE) {
	uip_ds6_if.addr_list[i].state = ADDR_PREFERRED;
      }
    }
  }
}
/*---------------------------------------------------------------------------*/
static int 
serial_input_byte(unsigned char c)
{
	int i=0;
	int t=0;
	uint8_t node_ip[39]; // 32(IP) + 6(:) + one for '\0' 	
	uip_ipaddr_t uip_node_ip;
	char *in_comm;//[3]; //2 char+(\n)
	in_comm = (char *) malloc(3);

	PRINTF("New data from serial port\n");
			
	if(c != '\n' && uart_buffer_index < UART_BUFFER_SIZE){
	  uart_buffer[uart_buffer_index++] = c;
	}
	else{
      uart_buffer[uart_buffer_index] = '\0';
      uart_buffer_index = 0;
      PRINTF("Received from UART (controller): %s\n",uart_buffer); 
		
		/* Start processing the message */
		while(uart_buffer[i]!='\0'){
			in_comm[0] = uart_buffer[0];
			in_comm[1] = uart_buffer[1]; // e.g. "SF"
			in_comm[2] = '\0';
			i = i+4; //jump the space char " "

			while(uart_buffer[i]!='\"' && uart_buffer[i]!=']'){   //copy val
				node_ip[t]=uart_buffer[i];
				PRINTF("buf_in:%u, node_ip[%u] %c\n",uart_buffer[i],t,node_ip[t]);
				t++;
				i++;
			}       
			/* BE CAREFUL: t=39, String has 39 elements */
			node_ip[t]='\0';  // DO WE NEED A TERMINATION CHARACTER ???
			PRINTF("END INCOMING IP\n");

/* TRANSFORMING THE LOCAL IP (fe80) BACK TO GLOBAL(fd00)! WORKS LIKE A CHARM */
			node_ip[1] = 'D';
			node_ip[2] = '0';

			/* Convertion from String to IPv6 */
		    if(uiplib_ip6addrconv(node_ip, &uip_node_ip) != 0 ){

			  uip_ip6addr_copy(&server_conn->ripaddr, &uip_node_ip);
			  PRINTF("IP server_con->ripaddr: ");
			  PRINT6ADDR(&server_conn->ripaddr);
			  PRINTF("\n");
			  uip_udp_packet_send(server_conn, "SP", sizeof("SP"));
			  uip_create_unspecified(&server_conn->ripaddr); //nullifies the IP
			}
			else{
				printf("Failed to transform IPv6 from ");
				int g;
				for (g = 0; g!='\"'; g++){
					printf("%c",node_ip[g]);
				}
				printf(". Output IP is ");
				printLongAddr(&uip_node_ip);
				printf("\nNo message was send!\n");
		   }
		   return 1;
		} //while uart_buffer
		i++;
		return 0;
   }// else
   return 0;
}
/*---------------------------------------------------------------------------*/
PROCESS_THREAD(udp_server_process, ev, data)
{

#define PRINTROUTES 1
#define PRINTNBRS 0

  static struct etimer periodic;
  static struct ctimer backoff_timer;
  
  uip_ipaddr_t ipaddr;
  struct uip_ds6_addr *root_if;

  PROCESS_BEGIN();

  PROCESS_PAUSE();

  SENSORS_ACTIVATE(button_sensor);

  PRINTF("UDP server started. nbr:%d routes:%d\n",
         NBR_TABLE_CONF_MAX_NEIGHBORS, UIP_CONF_MAX_ROUTES);

#if UIP_CONF_ROUTER
#if 0
/* Mode 1 - 64 bits inline */
   uip_ip6addr(&ipaddr, UIP_DS6_DEFAULT_PREFIX, 0, 0, 0, 0, 0, 0, 1);
#elif 1
/* Mode 2 - 16 bits inline */
  uip_ip6addr(&ipaddr, UIP_DS6_DEFAULT_PREFIX, 0, 0, 0, 0, 0x00ff, 0xfe00, 1);
#else
/* Mode 3 - derived from link local (MAC) address */
  uip_ip6addr(&ipaddr, UIP_DS6_DEFAULT_PREFIX, 0, 0, 0, 0, 0, 0, 0);
  uip_ds6_set_addr_iid(&ipaddr, &uip_lladdr);
#endif

  uip_ds6_addr_add(&ipaddr, 0, ADDR_MANUAL);
  root_if = uip_ds6_addr_lookup(&ipaddr);
  if(root_if != NULL) {
    //rpl_dag_t *dag; /* global to be used elsewhere
    dag = rpl_set_root(RPL_DEFAULT_INSTANCE,(uip_ip6addr_t *)&ipaddr);
    uip_ip6addr(&ipaddr, UIP_DS6_DEFAULT_PREFIX, 0, 0, 0, 0, 0, 0, 0);
    rpl_set_prefix(dag, &ipaddr, 64);
    printf("created a new RPL dag\n");
  } else {
    printf("failed to create a new RPL DAG\n");
  }
#endif /* UIP_CONF_ROUTER */
  
  print_local_addresses();

  /* The data sink runs with a 100% duty cycle in order to ensure high 
     packet reception rates. */
  NETSTACK_MAC.off(1);

  server_conn = udp_new(NULL, UIP_HTONS(UDP_CLIENT_PORT), NULL);
  if(server_conn == NULL) {
    printf("No UDP connection available, exiting the process!\n");
    PROCESS_EXIT();
  }
  udp_bind(server_conn, UIP_HTONS(UDP_SERVER_PORT));

  printf("Created a server connection with remote address ");
  printLongAddr(&server_conn->ripaddr);
  printf(" local/remote port %u/%u\n", UIP_HTONS(server_conn->lport),
         UIP_HTONS(server_conn->rport));

  /* Waiting to read from the serial port */
  uart1_set_input(serial_input_byte);
  
  etimer_set(&periodic, SEND_INTERVAL);
  while(1) {
    PROCESS_YIELD();

    if(ev == tcpip_event) {
      tcpip_handler();
    } 
    
    if(etimer_expired(&periodic)) {
      etimer_reset(&periodic);
      
      /* printing all enabled stats every &backoff_timer */
      ctimer_set(&backoff_timer, SEND_TIME, print_stats, NULL);	
		counter++; 
    }
  }//end while
  PROCESS_END();
}
/*---------------------------------------------------------------------------*/
