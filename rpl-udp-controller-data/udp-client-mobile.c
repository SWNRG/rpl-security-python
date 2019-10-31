#include "contiki.h"
#include "lib/random.h"
#include "sys/ctimer.h"
#include "net/ip/uip.h"
#include "net/ipv6/uip-ds6.h"
#include "net/ip/uip-udp-packet.h"
#include "sys/ctimer.h"

#ifdef WITH_COMPOWER
#include "powertrace.h"
#endif
#include <stdio.h>
#include <string.h>

#include "dev/serial-line.h"
#include "net/ipv6/uip-ds6-route.h"
#include "net/ipv6/uip-ds6-nbr.h"

#define UDP_CLIENT_PORT 8765
#define UDP_SERVER_PORT 5678

#define UDP_EXAMPLE_ID  190

//#define DEBUG DEBUG_FULL
#include "net/ip/uip-debug.h"

#ifndef PERIOD
#define PERIOD 60
#endif

#define START_INTERVAL		(15 * CLOCK_SECOND)
#define SEND_INTERVAL		(PERIOD * CLOCK_SECOND)
#define SEND_TIME		(random_rand() % (SEND_INTERVAL))
#define MAX_PAYLOAD_LEN		30

/* NODE IS MOBILE, HENCE SHOULD NOT BE CHOSEN AS FATHER */
#define RPL_CONF_LEAF_ONLY 1

static struct uip_udp_conn *client_conn;
static uip_ipaddr_t server_ipaddr;

/* George: Get the preffered parent, and the current own IP of the node */
#include "net/rpl/rpl-icmp6.c"
extern   rpl_parent_t *dao_preffered_parent;
extern   uip_ipaddr_t *dao_preffered_parent_ip;
extern   uip_ipaddr_t dao_prefix_own_ip;

/* George: Monitor this var. When changed, the node has changed parent */
static rpl_parent_t *my_cur_parent;
static uip_ipaddr_t *my_cur_parent_ip;
static int counter=0; //counting rounds. Not really needed

/* sink will ask ad-hoc for neibhbors. Use it with graph theory to find
 * intruders, and possible mobile nodes.
 */
static uint8_t send_neighbors = 0; // NOT USED CURRENTLY 

/*---------------------------------------------------------------------------*/
PROCESS(udp_client_process, "UDP client process");
AUTOSTART_PROCESSES(&udp_client_process);
/*---------------------------------------------------------------------------*/
static int seq_id;
static int reply;

static void
send_new_parent(uip_ipaddr_t *addr)
{
  unsigned char buf[50]; //dont forget, 50 chars
#define PRINT_PARENT 1

#ifdef PRINT_PARENT
  printf("NP ");
  printLongAddr(addr);
  printf(", sending to %d\n", server_ipaddr.u8[sizeof(server_ipaddr.u8) - 1]);
#endif

  sprintf(buf, "[NP:[%02x%02x:%02x%02x:%02x%02x:%02x%02x:%02x%02x:%02x%02x:%02x%02x:%02x%02x]", 
  		((uint8_t *)addr)[0], ((uint8_t *)addr)[1], ((uint8_t *)addr)[2], ((uint8_t *)addr)[3], 
  		((uint8_t *)addr)[4], ((uint8_t *)addr)[5], ((uint8_t *)addr)[6], ((uint8_t *)addr)[7], 
  		((uint8_t *)addr)[8], ((uint8_t *)addr)[9], ((uint8_t *)addr)[10], ((uint8_t *)addr)[11], 
  		((uint8_t *)addr)[12], ((uint8_t *)addr)[13], ((uint8_t *)addr)[14], ((uint8_t *)addr)[15] 
  	);

  uip_udp_packet_sendto(client_conn, buf, strlen(buf),
  			&server_ipaddr, UIP_HTONS(UDP_SERVER_PORT));
}
/*---------------------------------------------------------------------------*/
static void
tcpip_handler(void)
{
  char *str;

  if(uip_newdata()) {
    str = uip_appdata;
    str[uip_datalen()] = '\0';
    reply++;
    
	 if(str[0] == 'S' && str[1] == 'P'){
		 printf("Responding to sink's probe about my parent\n"); 
		 /* Send the parent again, after sink's request */
		 send_new_parent(my_cur_parent_ip);  	 
	 }else if(str[0] == 'S' && str[1] == 'N'){ 
			printf("Sink is probing my neighbors\n"); //sink asking for neighbors		
			send_neighbors = 1; //trigger the nbr sending below		
	 }else{
	 
	 	printf("DATA recv '%s' (s:%d, r:%d)\n", str, seq_id, reply);
	 	
	 	
	 }
  }
}
/*---------------------------------------------------------------------------*/
static void
send_packet(void *ptr)
{
  char buf[MAX_PAYLOAD_LEN];

#ifdef SERVER_REPLY
  uint8_t num_used = 0;
  uip_ds6_nbr_t *nbr;

  nbr = nbr_table_head(ds6_neighbors);
  while(nbr != NULL) {
    nbr = nbr_table_next(ds6_neighbors, nbr);
    num_used++;
  }
/*
  if(seq_id > 0) {
    ANNOTATE("#A r=%d/%d,color=%s,n=%d %d\n", reply, seq_id,
             reply == seq_id ? "GREEN" : "RED", uip_ds6_route_num_routes(), num_used);
  }
 */
#endif /* SERVER_REPLY */

  seq_id++;
  PRINTF("DATA send to %d 'Hello %d'\n",
         server_ipaddr.u8[sizeof(server_ipaddr.u8) - 1], seq_id);
  sprintf(buf, "Hello %d from the client", seq_id);
  uip_udp_packet_sendto(client_conn, buf, strlen(buf),
                        &server_ipaddr, UIP_HTONS(UDP_SERVER_PORT));
}
/*---------------------------------------------------------------------------*/
static void
print_local_addresses(void)
{
  int i;
  uint8_t state;

  PRINTF("Client IPv6 addresses: ");
  for(i = 0; i < UIP_DS6_ADDR_NB; i++) {
  
  	 //printf("int i: %d\n",i);
  	 
    state = uip_ds6_if.addr_list[i].state;
    if(uip_ds6_if.addr_list[i].isused &&
       (state == ADDR_TENTATIVE || state == ADDR_PREFERRED)) {
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
static void
set_global_address(void)
{
  uip_ipaddr_t ipaddr;

  uip_ip6addr(&ipaddr, UIP_DS6_DEFAULT_PREFIX, 0, 0, 0, 0, 0, 0, 0);
  uip_ds6_set_addr_iid(&ipaddr, &uip_lladdr);
  uip_ds6_addr_add(&ipaddr, 0, ADDR_AUTOCONF);

/* The choice of server address determines its 6LoWPAN header compression.
 * (Our address will be compressed Mode 3 since it is derived from our
 * link-local address)
 * Obviously the choice made here must also be selected in udp-server.c.
 *
 * For correct Wireshark decoding using a sniffer, add the /64 prefix to the
 * 6LowPAN protocol preferences,
 * e.g. set Context 0 to fd00::. At present Wireshark copies Context/128 and
 * then overwrites it.
 * (Setting Context 0 to fd00::1111:2222:3333:4444 will report a 16 bit
 * compressed address of fd00::1111:22ff:fe33:xxxx)
 *
 * Note the IPCMV6 checksum verification depends on the correct uncompressed
 * addresses.
 */
 
#if 0
/* Mode 1 - 64 bits inline */
   uip_ip6addr(&server_ipaddr, UIP_DS6_DEFAULT_PREFIX, 0, 0, 0, 0, 0, 0, 1);
#elif 1
/* Mode 2 - 16 bits inline */
  uip_ip6addr(&server_ipaddr, UIP_DS6_DEFAULT_PREFIX, 0, 0, 0, 0, 0x00ff, 0xfe00, 1);
#else
/* Mode 3 - derived from server link-local (MAC) address */
  uip_ip6addr(&server_ipaddr, UIP_DS6_DEFAULT_PREFIX, 0, 0, 0, 0x0250, 0xc2ff, 0xfea8, 0xcd1a); //redbee-econotag
#endif
}
/*---------------------------------------------------------------------------*/



/****************NOT USED! Direct children, only once *******************/
static void 
print_all_neighbors(void)
{
	uip_ds6_nbr_t *least_expiring_nbr;
	uint8_t *state;
	uip_ds6_nbr_t *nbr = nbr_table_head(ds6_neighbors);
	
	printf("My neighbors only: \n");    	
	
	while(nbr != NULL) {
		printf("NN: ");
		printLongAddr(&nbr->ipaddr);
		state = nbr->state;
		printf(", state %d", state);

		printf("\n");
		//clock_time_t curr = stimer_remaining(&nbr->reachable);
		//printf(", time %d \n", &nbr->reachable);
		nbr = nbr_table_next(ds6_neighbors, nbr);
	}
	
	//least_expiring_nbr = uip_ds6_get_least_lifetime_neighbor();
	/*
	printf("least expiring nbr: ");
	printLongAddr(&least_expiring_nbr->ipaddr);
	printf(" %d\n",nbr->reachable);
	*/
	printf("End of neighbors\n"); 	

}
/*-------------- All direct children and their descentants -------------------
uip_ds6_nbr_t *
uip_ds6_get_least_lifetime_neighbor(void)
{
  uip_ds6_nbr_t *nbr = nbr_table_head(ds6_neighbors);
  uip_ds6_nbr_t *nbr_expiring = NULL;
  while(nbr != NULL) {
    if(nbr_expiring != NULL) {
      clock_time_t curr = stimer_remaining(&nbr->reachable);
      if(curr < stimer_remaining(&nbr->reachable)) {
        nbr_expiring = nbr;
      }
    } else {
      nbr_expiring = nbr;
    }
    nbr = nbr_table_next(ds6_neighbors, nbr);
  }
  return nbr_expiring;
}
-------------- All direct children and their descentants -------------------*/

static void 
monitor_DAO(void)
{
/* dont forget: parent_ip = rpl_get_parent_ipaddr(parent->dag->preferred_parent)*/

#define PRINT_CHANGES 1

	/* In contiki, you can directly compare if(parent == parent2) */
	if(my_cur_parent != dao_preffered_parent){
#ifdef PRINT_CHANGES
		printf("RPL-G: Change detected. Old parent->");
		printLongAddr(my_cur_parent_ip);
		printf(", new->");
		printLongAddr(dao_preffered_parent_ip);
		printf("\n");
#endif
		my_cur_parent = dao_preffered_parent;
		my_cur_parent_ip = dao_preffered_parent_ip;
		
		/* send the parent on application level back to sink */
		send_new_parent(my_cur_parent_ip);
	}
}
/*---------------------------------------------------------------------------*/
PROCESS_THREAD(udp_client_process, ev, data)
{
  static struct etimer periodic;
  static struct ctimer backoff_timer;
#if WITH_COMPOWER
  static int print = 0;
#endif

  PROCESS_BEGIN();

  PROCESS_PAUSE();

  printf("UIP_ND6_SEND_NA %d\n", UIP_ND6_SEND_NA);
  printf("UIP_ND6_SEND_NS %d\n", UIP_ND6_SEND_NS); 


  /* If RPL_LEAF_ONLY == 1, node as a leaf cannot be chosen as father */
  printf("RPL_LEAF_ONLY: %d, ",RPL_LEAF_ONLY); // TO DO: It does not seem to work
  
  rpl_set_mode(2); /* leaf mode =2, feather =1 */
  printf("Leaf MODE: %d\n",rpl_get_mode());
    


  set_global_address();

  printf("UDP client process started nbr:%d routes:%d\n",
         NBR_TABLE_CONF_MAX_NEIGHBORS, UIP_CONF_MAX_ROUTES);

  print_local_addresses();

  /* new connection with remote host */
  client_conn = udp_new(NULL, UIP_HTONS(UDP_SERVER_PORT), NULL); 
  if(client_conn == NULL) {
    printf("No UDP connection available, exiting the process!\n");
    PROCESS_EXIT();
  }
  udp_bind(client_conn, UIP_HTONS(UDP_CLIENT_PORT)); 

  printf("Created a connection with the server ");
  printLongAddr(&client_conn->ripaddr);
  printf(" local/remote port %u/%u\n",
			UIP_HTONS(client_conn->lport), UIP_HTONS(client_conn->rport));


  etimer_set(&periodic, SEND_INTERVAL);
  while(1) {
    PROCESS_YIELD();
    
    /* monitor parent changes & send it via UDP to sink */
    monitor_DAO();
    
    if(ev == tcpip_event) {
      tcpip_handler();
    }

    if(etimer_expired(&periodic)) {
      etimer_reset(&periodic);
      
      /* sending regular data to sink (e.g. temperature measurements) */
      ctimer_set(&backoff_timer, SEND_TIME, send_packet, NULL);

		/* First you have to make sure that old neighbors are removed.
		 * This is connected with UIP_ND6_SEND_NA which is not enabled by default
		 */
      //print_all_neighbors();
      
      counter++;
/* *************** STATISTICS ENABLED BY THE SINK ************************** */
      printf("R:%d, udp_sent:%d\n",counter,uip_stat.udp.sent);
    	printf("R:%d, udp_recv:%d\n",counter,uip_stat.udp.recv);	
    
    	printf("R:%d, icmp_sent:%d\n",counter,uip_stat.icmp.sent);
    	printf("R:%d, icmp_recv:%d\n",counter,uip_stat.icmp.recv);
/* *************** STATISTICS ENABLED BY THE SINK ************************** */      
    }
  }//end while
  PROCESS_END();
}
/*---------------------------------------------------------------------------*/
