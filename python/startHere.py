#!/usr/bin/python

import serial
import time
import sys
from getSerialPortCooja import get1stpts
import networkx as nx
import matplotlib.pyplot as plt


#-------------------------------------------------------------------#
def getOrphanNodes():
	for node in G.nodes():
		predecessors = list(G.predecessors(node)) # parents
		successors = list(G.successors(node))	  # children
		in_degree = len(predecessors) 
		out_degree = len(successors) # NOT USED
		
		if in_degree == 0:
			if (node != sink_ip): # sink is always an orphan
				print "Probing orphan node : ", node
				# send a probe message to the node. Such a node, 
				# is obviously connected to the network, but we never 
				# got his father info...	
				probeMsg = "SP "+node+"\n"
				#print "Probing msg: ", probeMsg
				ser.write(probeMsg) #SP: Send Parent
#-------------------------------------------------------------------#				
def shortName(nodeIP):
	short_name = nodeIP[1].rsplit(":",1)
	return short_name[1]
#-------------------------------------------------------------------#	
def printGraph():
	counter = 0
	print "--------EDGES----------------------"
	for n1, n2 in G.edges():
		counter+=1
		#print counter," ", G.node[n1]['s_name'],"-->", G.node[n2]['s_name']
		print counter, " ",n1," --> ",n2
	print "--------END OF GRAPH---------------"	
#-------------------------------------------------------------------#	
def printNodes():
	if G.nodes():
		for n in G.nodes():
			print "node: ",n
#-------------------------------------------------------------------#
def getSerPort():
	port = "" # serial port of cooja sink mode
	while not port: #if cooja port is not there, dont continue
		port = get1stpts()
		try:
			port = get1stpts()
		except serial.SerialException as e:
			print "Cooja Port Error ", e

	print "\nCooja pts port found, continuing...\n"
	return serial.Serial(port,  115200)#, timeout = 1)
#-------------------------------------------------------------------#
def removePredecessors(nodeIn):
	try:
		predecessors = [pred for pred in G.predecessors(nodeIn)]
		#print "Deleting predecessors of ",nodeIn,":"
		#print predecessors
		
		for p in predecessors:
			print "Removing OLD edge ",p,"-->",nodeIn
			G.remove_edge(p,nodeIn)
	except Exception as e:
		print "Failed to delete precessor(s) of ",nodeIn,": ",e
#-------------------------------------------------------------------#	
	
G = nx.DiGraph() #networkx graph

sink_ip 	= "" # globaly used 
noSink = 1 #there is no active sink yet
printSinkMsg = ""
printGraphOn = 0

print "\n...INITIALIZING RPL OUTPUT READING...\n"
ser = getSerPort() #get the pts (cooja) serial port automatically

while True:
	try: 
		readOut = ser.readline().rstrip('\n')#.decode('ascii')
		#print readOut
		
		if(readOut.startswith("Tentative ")):# and noSink):
		
			sink_ip_2 = readOut.split("Tentative link-local IPv6 address ",1)			
			sink_ip = "["+sink_ip_2[1]+"]"
			s_name = sink_ip_2[1].rsplit(":",1)
			s_name = s_name[1]
			#print "sink s_name:",s_name

			if(not printSinkMsg):
			
				print "MESSAGE ONCE ONLY-->Sink found: "+sink_ip+" short "+s_name
				printSinkMsg = 1
			
			noSink = 0 #sink found. no need to reprobe
			G.add_node(sink_ip, name = "sink", s_name=s_name)
			
#-------not used. It is problematic. Check udp-sink for details	----------#
		elif(readOut.startswith("Sinks child")):
			sinks_child = readOut.split("Sinks child: ",1)
			sinks_child = sinks_child[1]
			print "Sink's direct child: "+sinks_child
#-------------------------------------------------------------------------#

		elif(readOut.startswith("Route")):		
			route = readOut.split("Route: ",1)
			nodes = route[1]
			nodes = nodes.split(" ",1)
			child = nodes[0] #child
			node = nodes[1]
			node = node.split(" ",1)
			lt = node[1]
			node = node[0] #father
			lt = lt.split(":",1)
			lt = lt[1]

			if ( child == node ):
				if (child not in G.nodes()):
					#print("New child found: ", child, ", short ", s_name)
					s_name = (child[1].rsplit(":",1))
					s_name = s_name[1]
					print "Adding a new direct child"
					G.add_node(child, time=lt, s_name = s_name )

				if ( not G.edges( sink_ip, child ) ): # no need to delete parent
					print "Adding sink-->child: ", sink_ip,"-->",child	
					G.add_edge( sink_ip, child ) # from --> to

		elif(readOut.startswith("[NP")):
			np = readOut.split("[NP:",1)
			neig = np[1] 
			neig = neig.split(" ",1)
			des = neig[1] # CHILD = des[1]
			des = des.split("from ",1)
			neig = neig[0]	# FATHER = neig
			# when no route yet, this IP comes up. Not needed...
			if neig != "[0100:8000:4030:0000:0000:0000:0000:0000]" :
				if (neig == des[1]): # direct child of sink
					if (neig not in G.nodes()):
						s_name = (neig.rsplit(":",1))
						s_name = s_name[1]
						print "Adding a new sink's direct child: ", neig, ", short ",s_name 
						G.add_node(neig, s_name = s_name)
						
					else:
						#print "Deleting predecessors of ", des[1]
						removePredecessors(des[1])
						
					# in both cases add the edge	
					print "Adding sink-->child ",sink_ip,"-->",des[1]
					G.add_edge( sink_ip, des[1] )	#sink --> des[1]
					printGraph()
				
				else: # not a direct child of sink
					if (neig not in G.nodes()):
						s_name = (neig.rsplit(":",1))
						s_name = s_name[1].rsplit("]",1)
						s_name = s_name[0]
						print "New predessecor adding: ", neig, ", short ", s_name
						G.add_node(neig, s_name = s_name)

					if (des[1] not in G.nodes()):
						s_name = des[1].rsplit(":",1)
						s_name = s_name[1].rsplit("]",1)
						s_name = s_name[0]
						G.add_node(des[1], s_name = s_name )
						print "New successor added: ",des[1],", short ",s_name 

					if not G.has_edge(neig, des[1]):			
						#delete a possible old edge of neig
						removePredecessors(des[1])
						# NOT a direct child of sink
						print "Adding new edge ",neig,"-->",des[1]
						G.add_edge( neig, des[1] ) # from --> to	
						printGraph()						
						
					#else:
						#print "Edge exists: ", neig,"-->",des[1]

						
		if(noSink): # Safety measure: after 2-3 rounds, it should dissapear
			print ("...Sink not set yet...")
			pass #until it finds the sink
		
		# check for orphan nodes and probe them
		getOrphanNodes()

		'''
		# TO DO: what to do with isolates??? Is there something to DO???	
		if(nx.isolates(G)):
			for node in nx.isolates(G):
				print("Isolated node ", node)
				# TO DO: send a probing message to the sink
		'''			
		'''
		else:
			for child in G.nodes():
				print "Predessecors of ",child
				for n in G.predecessors(child):  #maybe an if to remove isolated nodes???
					print n
				print "----------End Predecessors--------\n"
				
				print "---------SUCCESSORS of ",child,"------------"
				for s in G.successors(child):
					print s
				print "----------End SUCCESSORS------------\n"
		'''		

		'''
		print "--------------- out_edges------------"
		print G.out_edges()
		print "--------------- out_edges------------"
		'''
			
		
		'''
		if G.predecessors(n):
			#we must delete them! if he found a new father !!!!!!!
			print
			
		if (G.out_edges(node)):
			print
		'''
		
		
		# remove loops. USE IT AS SOON AS YOU SEE ONE LOOP !!!!!!!!!!
		# G.remove_edges_from(G.selfloop_edges())
		# or
		#for u, v in G.edges_iter():
		#	if u == v: 
		#		G.remove_edge(u,v)
		
		
		
		
		



		if(not noSink):
			nx.draw(G,with_labels=True)
			#plt.savefig("graph.png")
			#plt.show()
		
		
		#for n in G.nodes():
		#	print n	
				
		#print ('Graph nodes ', G.number_of_nodes() )
		#print( 'Graph edges ', G.number_of_edges() )
		#print("Graph adj table: ", G.adj)
		
	except IOError as e:
		print ("I/O error ",e)
	except ValueError:
		print ("Value problem.")
	except Exception as e:
		print ("Error ",e)
		time.sleep(4)
		pass
