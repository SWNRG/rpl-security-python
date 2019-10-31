#!/usr/bin/python

import serial
import time
import sys
from getSerialPortCooja import get1stpts
import networkx as nx
import matplotlib.pyplot as plt
import socket

#-------------------------------------------------------------------#
def getICMP_stats(node):
	probeMsg = "SI "+node+"\n"
	#print "Probing msg: ", probeMsg
	ser.makefile().write(probeMsg) #SP: Send Parent
#-------------------------------------------------------------------#
def getUDP_stats(node):
	probeMsg = "SU "+node+"\n"
	#print "Probing msg: ", probeMsg
	ser.makefile().write(probeMsg) #SP: Send Parent
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
				ser.makefile().write(probeMsg) #SP: Send Parent
#-------------------------------------------------------------------#				
def shortName(nodeIP):
	short_name = nodeIP[1].rsplit(":",1)
	return short_name[1]
#-------------------------------------------------------------------#	
def printGraph(rounds):
	counter = 0
	print "---Round: ", rounds,"------EDGES------------"
	for n1, n2 in G.edges():
		counter+=1
		#print counter," ", G.node[n1]['s_name'],"-->", G.node[n2]['s_name']
		print counter, " ",n1," --> ",n2
	print "--------------END OF GRAPH---------------"	
#-------------------------------------------------------------------#	
def printNodes():
	if G.nodes():
		for n in G.nodes():
			print "node: ",n
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
		print "Failed to delete predecessor(s) of ",nodeIn,": ",e
#-------------------------------------------------------------------#	
def getTunslip6Port():
	'''
	Creates an array of ALL available tunslip6 ports.
	all tunsilp6 availiable ports wiil be in d[], 
	but only the first port is returned
	'''
	address = "localhost"
	port = 60001
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.settimeout(3.0)
		sock.connect((address, port))
		if(sock.makefile()):
			print "Open port found at ",address,", port ",port
		#sock.close() # it returns "bad file decsriptor..."
		return sock#.makefile()	
	except Exception as e:
		print ("get cooja Port Error: ", e)
#-------------------------------------------------------------------#	
	
G = nx.DiGraph() #networkx graph

sink_ip 	= "" # globaly used 
noSinkYet = 1 #there is no active sink yet
sinkNeverFound = 0
counter = 0
rounds = 0

printSinkMsg = ""
printGraphOn = 0

print "\n...INITIALIZING RPL OUTPUT READING...\n"
ser = ""
while (not ser):
	ser = getTunslip6Port()	
	#time.sleep(2)
print "Serial port found: ", ser

while True:
	try:
		rounds+=1

		if (rounds%6==0): # if it fires on every round, cooja crashes
			# check for orphan nodes and probe them
			getOrphanNodes()
		#if the sink's IP is not probed, set it up to 0101
		if(counter >5): 
			sinkNeverFound = 1
			
		readOut = ser.makefile().readline().rstrip('\n')#.decode('ascii')

#============== Sent/Recvd UDP packets per node ==========================
		if(readOut.startswith("[SU:")):
			msg = readOut.split("[SU:",1)	
			print ("SU msg: ", msg[1])
			msgAll = msg[1].split("]",1)
			UDP_all = msgAll[0]
			clientIP = msgAll[1]
			nums=UDP_all.split(" ",1)
			print "nums",nums
			sentUDP = nums[0]
			print "sentUDP",sentUDP
			recvUDP = nums[1]
			print "recvUDP", recvUDP
#============== Sent/Recvd ICMP packets per node ==========================
		if(readOut.startswith("[SI:")):
			msg = readOut.split("[SI:",1)	
			print ("SI msg: ", msg[1])
			msgAll = msg[1].split("]",1)
			UDP_all = msgAll[0]
			clientIP = msgAll[1]
			nums=UDP_all.split(" ",1)
			print "nums",nums
			sentICMP = nums[0]
			print "sentICMP",sentICMP
			recvICMP = nums[1]
			print "recvUDP", recvICMP
#=============== Sink's IP ADDRESS (If found)==============================
		if(readOut.startswith("Tentative ")):# and noSinkYet):		
			sink_ip_2 = readOut.split("Tentative link-local IPv6 address ",1)			
			sink_ip = "["+sink_ip_2[1]+"]"
			s_name = sink_ip_2[1].rsplit(":",1)
			s_name = s_name[1]
			#print "sink s_name:",s_name
		
			if(not printSinkMsg):			
				print "MESSAGE ONCE ONLY-->Sink found: "+sink_ip+" short "+s_name
				printSinkMsg = 1
			
			noSinkYet = 0 #sink found. no need to reprobe
			G.add_node(sink_ip, name = "sink", s_name=s_name)
			
		if (sinkNeverFound): #if sink was not found after a while		
			sink_ip = "[fe80:0000:0000:0000:0212:7401:0001:0101]"
			s_name = "0101"		
#=========not used. It is problematic. Check udp-sink for details==========
		elif(readOut.startswith("Sinks child")):
			sinks_child = readOut.split("Sinks child: ",1)
			sinks_child = sinks_child[1]
			print "Sink's direct child: "+sinks_child			
#======== Routes per node =================================================
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
					s_name = (child.rsplit(":",1))
					s_name = s_name[1]
					#print("New child found: ", child, ", short ", s_name)
					print "Adding a new direct child ", child
					G.add_node(child, time=lt, s_name = s_name )

				if ( not G.edges( sink_ip, child ) ): # no need to delete parent
					print "Adding sink-->child: ", sink_ip,"-->",child	
					G.add_edge( sink_ip, child ) # from --> to
#==========Each node sends a new parent if found ==========================
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
#============ Removing old father if new one found =======================						
					else:
						#print "Deleting predecessors of ", des[1]
						removePredecessors(des[1])
						
					# in both cases add the edge	
					print "Adding sink-->child ",sink_ip,"-->",des[1]
					G.add_edge( sink_ip, des[1] )	#sink --> des[1]
					printGraph(rounds)
				
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
						printGraph(rounds)						
						
					#else:
						#print "Edge exists: ", neig,"-->",des[1]
						
		if(noSinkYet): # Safety measure: after 2-3 rounds, it should dissapear
			counter+=1
			print ("...Sink not set yet...")
			#continue #until it finds the sink


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
		
		
		
		
		



		if(not noSinkYet):
			nx.draw(G,with_labels=True)
			#plt.savefig("graph.png")
			#plt.show()
		
		
		#for n in G.nodes():
		#	print n	
				
		#print ('Graph nodes ', G.number_of_nodes() )
		#print( 'Graph edges ', G.number_of_edges() )
		#print("Graph adj table: ", G.adj)
		
	except IOError as e:
		pass #print ("I/O error ",e)
	except ValueError as e :
		print ("Value problem.",e)
	#except Exception as e:
	#	print ("Error ",e)
		#time.sleep(4)
		#pass

