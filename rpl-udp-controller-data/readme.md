Insert this folder into contiki/examples/ipv6
run the *.csc files in cooja.
Remember, the sink is sending all messages to the serial
port, where a controller must read them.
The sink also receives messages from the serial port,
and then asks nodes accordingly.
There is no direct communication between controller <-> nodes.

RPL in storing mode does not know the full network. It
only knows the direct children of the sink, and the sink's 
descendants (not knowing how "deep down" they are).
In other words, the sink has to level of direct children and grandchildren no matter how many generations after.

On the application level, udp messages are exchanged betweenbsink <->nodes to communicate the missing information.
Each node sends a UDP packet to the sink mentioning the node'sending own father. The message is send once at the 
beggining of the simulation, and upon request of the sink.

Other info can also be communicated via those UDP messages, like for example ETX, color, energy, etc.

The idea is for the controller to construct a full graph of
the network, been in communication only with the sink
