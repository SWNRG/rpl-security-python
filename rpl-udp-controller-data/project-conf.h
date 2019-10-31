
#ifndef PROJECT_CONF_H_
#define PROJECT_CONF_H_


/* Enable STATISTICS: it will give you UDP and ICMP per node */
#define UIP_CONF_STATISTICS 1  

#undef UIP_CONF_ND6_SEND_NS
#define UIP_CONF_ND6_SEND_NS 0
/*
#undef UIP_CONF_ND6_SEND_NA
#define UIP_CONF_ND6_SEND_NA 1
*/

/* inside rpl-mrhof.c you can enable printing details (rank) of chosen parent 
 * Good for monitoring malicious node "destructive force".
 * Remember, RPL can detect loops and avoid them, so eventually there will be
 * one at least connection tot he sink, even if the malicious advertises low rank
 */
#ifndef PRINT_CHOOSING_PARENT_DETAILS
#define PRINT_CHOOSING_PARENT_DETAILS 0
#endif



#ifndef WITH_NON_STORING
#define WITH_NON_STORING 0 /* Set this to run with non-storing mode */
#endif /* WITH_NON_STORING */

/* George print only the last part of the address (e.g. 02). Handy for debugging */
#ifndef printShortAddr
#define printShortAddr(addr) printf(" %02x ",((uint8_t *)addr)[15])
#endif
/* Printf full IPv6 address */
#define printLongAddr(addr) printf("[%02x%02x:%02x%02x:%02x%02x:%02x%02x:%02x%02x:%02x%02x:%02x%02x:%02x%02x]", ((uint8_t *)addr)[0], ((uint8_t *)addr)[1], ((uint8_t *)addr)[2], ((uint8_t *)addr)[3], ((uint8_t *)addr)[4], ((uint8_t *)addr)[5], ((uint8_t *)addr)[6], ((uint8_t *)addr)[7], ((uint8_t *)addr)[8], ((uint8_t *)addr)[9], ((uint8_t *)addr)[10], ((uint8_t *)addr)[11], ((uint8_t *)addr)[12], ((uint8_t *)addr)[13], ((uint8_t *)addr)[14], ((uint8_t *)addr)[15])

#ifndef SERVER_REPLY
#define SERVER_REPLY 1
#endif

#undef NBR_TABLE_CONF_MAX_NEIGHBORS
#undef UIP_CONF_MAX_ROUTES

#ifdef TEST_MORE_ROUTES
/* configure number of neighbors and routes */
#define NBR_TABLE_CONF_MAX_NEIGHBORS     10
#define UIP_CONF_MAX_ROUTES   30
#else
/* configure number of neighbors and routes */
#define NBR_TABLE_CONF_MAX_NEIGHBORS     10
#define UIP_CONF_MAX_ROUTES   10
#endif /* TEST_MORE_ROUTES */

#undef NETSTACK_CONF_RDC
#define NETSTACK_CONF_RDC     nullrdc_driver
#undef NULLRDC_CONF_802154_AUTOACK
#define NULLRDC_CONF_802154_AUTOACK       1

/* Define as minutes */
#define RPL_CONF_DEFAULT_LIFETIME_UNIT   60

/* 10 minutes lifetime of routes */
#define RPL_CONF_DEFAULT_LIFETIME        10

#define RPL_CONF_DEFAULT_ROUTE_INFINITE_LIFETIME 1

#if WITH_NON_STORING
#undef RPL_NS_CONF_LINK_NUM
#define RPL_NS_CONF_LINK_NUM 40 /* Number of links maintained at the root. Can be set to 0 at non-root nodes. */
#undef UIP_CONF_MAX_ROUTES
#define UIP_CONF_MAX_ROUTES 0 /* No need for routes */
#undef RPL_CONF_MOP
#define RPL_CONF_MOP RPL_MOP_NON_STORING /* Mode of operation*/
#endif /* WITH_NON_STORING */

#endif
