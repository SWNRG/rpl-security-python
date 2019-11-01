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
	#print "getICMP_stats msg: ", probeMsg
	ser.makefile().write(probeMsg) #SP: Send Parent
#-------------------------------------------------------------------#
def getUDP_stats(node):
	probeMsg = "SU "+node+"\n"
	#print "getUDP_stats msg: ", probeMsg
	ser.makefile().write(probeMsg) #SP: Send Parent
#-------------------------------------------------------------------#
def getOrphanNodes(ser, counter):
#send a probe message to the node. Such a node, is obviously connected 
#to the network, but we never got his father info...
	for node in G.nodes():
			predecessors = list(G.predecessors(node)) # parents
			successors = list(G.successors(node))	  # children
			in_degree = len(predecessors) 
			out_degree = len(successors) # NOT USED
			
			printSmallNames(counter)
									
			if in_degree == 0:
				if (node != sink_ip): # sink is always an orphan
					try:
						#print "Node.probed:",G.node[node]['probed']
						if(G.node[probed]>counter-5):							
							probeMsg = "SP "+node+"\n"
							print "Probing msg: ", "SP ",node
							ser.send(probeMsg.encode())
							G.add_node(node, probed = counter)
							#delay a bit. Looks like UART is ok now!
							time.sleep(0.5)	
						else:
							G.add_node(node, probed=counter)
					except Exception as e:
						print "Exception:",e
						"Node:",node," ERROR PROBING"
					finally:
						print "Adding node: ",G.node[node]['s_name']
						G.add_node(node, probed=0)
						print "Added node: ",node," ,probed=",G.node[node]['probed']
						
#-------------------------------------------------------------------#						
def s_name2dec(n1):
	num1 = G.node[n1]['s_name'][2]
	num2 = G.node[n1]['s_name'][3]
	dec_name = int(str(num1)+str(num2),16) #int(s, 16) from hex to dec
	return dec_name
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
		#print counter," ", G.node[n1]['s_name'],"<---", G.node[n2]['s_name']
		print counter, " ",n1," <--- ",n2
	print "--------------END OF GRAPH---------------\n"	
#-------------------------------------------------------------------#	
def printNodes():
	if G.nodes():
		for n in G.nodes():
			print "node: ",n
#-------------------------------------------------------------------#	
def printSmallNames(rounds):
	counter = 0
	print "--R: ", rounds,", GRAPH------------------"
	for n1, n2 in G.edges():
		counter+=1
		node1 = s_name2dec(n1)
		node2 = s_name2dec(n2)
		#print counter," ", G.node[n1]['s_name'],"<---", G.node[n2]['s_name']
		print counter,"\t", node1,"<---", node2
	print "--------------END OF GRAPH---------------"	
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
def getCoojaPort():
	server_address = ("localhost",60001)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	con = False
	while (not con):
		try:
			sock.connect(server_address)
			con = True
			print "Open port found at ",server_address
		except Exception as e:
			print ("get cooja Port Error: ", e)
	return sock
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
ser = getCoojaPort()
		
while True:
	try:
		rounds+=1
#======== Reading every incoming line======================================		
		readOut = ser.makefile().readline().rstrip('\n')#.decode('ascii')
		#print readOut,"\n"
#==========================================================================		
		if (rounds%6==0): # if it fires on every round, cooja crashes
			# check for orphan nodes and probe them each one every five rounds
			getOrphanNodes(ser,rounds)
#======= extra safety: edges = nodes -1 ===================================
			if (G.number_of_edges()!= G.number_of_nodes()-1):
				print "Iregularity: edges:",G.number_of_edges(),"nodes:",G.number_of_nodes()	
#=============== Setting up the sink if not found after a few rounds=======
		if(noSinkYet): # Safety measure: after 2-3 rounds, it should disappear
			counter+=1
			print ("...Sink not set yet...")
			#continue #until it finds the sink	
		#if the sink's IP is not probed, set it up to 0101
		if(counter >5): 
			sinkNeverFound = 1
		if (sinkNeverFound): #if sink was not found after a while
			sink_ip = "[fe80:0000:0000:0000:0212:7401:0001:0101]"
			print "setting sink: ",sink_ip
			s_name = "0101"			
#============== Sent/Recvd UDP packets FROM node ==========================
		if(readOut.startswith("[SU:")):
			msg = readOut.split("[SU:",1)	
			msgAll = msg[1].split("]",1)
			UDP_all = msgAll[0]
			clientIP = msgAll[1]
			clientIP = clientIP.split("from ",1)
			clientIP = clientIP[1]
			nums=UDP_all.split(" ",1)
			sentUDP = nums[0]
			recvUDP = nums[1]			
			# what to do with the above? In G graph or in dictionary?
			#G.add_node(clientIP, sentUDP = sentUDP, recvUDP = recvUDP)
#============== Sent/Recvd ICMP packets FROM node ==========================
		elif(readOut.startswith("[SI:")):
			msg = readOut.split("[SI:",1)	
			msgAll = msg[1].split("]",1)
			UDP_all = msgAll[0]
			clientIP = msgAll[1]
			clientIP = clientIP.split("from ",1)
			clientIP = clientIP[1]
			nums=UDP_all.split(" ",1)
			sentICMP = nums[0]
			recvICMP = nums[1]
			# what to do with the above? In G graph or in dictionary?
			#G.add_node(clientIP, sentICMP = sentICMP, recvICMP = recvICMP)
#=============== Sink's IP ADDRESS (If found)==============================
		elif(readOut.startswith("Tentative ")):# and noSinkYet):		
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
						print "Deleting predecessors of ", des[1]
						removePredecessors(des[1])
						
					# in both cases add the edge	
					print "Adding sink-->child ",sink_ip,"-->",des[1]
					G.add_edge( sink_ip, des[1] )	#sink --> des[1]
#============ Printing network graph ====================================
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
						print "Adding new edge ",s_name2dec(neig),"-->",s_name2dec(des[1])
						
						G.add_edge( neig, des[1] ) # from --> to							
#=============PRINTING THE GRAPH============================================						
						#ONLY HERE THE GRAPH PRINTS
						#printGraph(rounds)		
						
						
						
						
						
					#else:
						#print "Edge exists: ", neig,"-->",des[1]

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
		
		
		'''
		print "start of nodes"
		countR =0
		for n in sorted(G.nodes()):
			countR+=1
			print countR," ",n	
		print "end of nodes"
		'''		
				
				
				
				
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

