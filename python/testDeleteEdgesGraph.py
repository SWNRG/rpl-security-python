#!/usr/bin/python

import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()

G.add_node(1)

G.add_node(8, time=34)
G.add_edge(1, 8)

G.add_node(3)
G.add_node(5)
G.add_edge(3, 5)

G.add_edge(1, 3)

#self loop
G.add_edge(3, 3)
print "with loop 3-->3"
for node in G.nodes(): # with a loop 3-->3
	for p in G.predecessors(node):
		print "predeces-->node: ",p,"-->",node
#remove the loop
G.remove_edges_from(G.selfloop_edges())
print "loop 3-->3 removed"
for node in G.nodes(): # with a loop 3-->3
	for p in G.predecessors(node):
		print "predeces-->node: ",p,"-->",node
print

G.add_node(2)
G.add_edge(3, 2)

G.add_node(4)
G.add_edge(2, 4)

G.add_node(6)
G.add_edge(5, 6)

G.add_node(7)
G.add_edge(5, 7)

G.add_node(9)
G.add_edge(3,9)

G.add_node(10) #isolated


G.remove_edges_from(G.selfloop_edges())


for node in G.nodes():
	for p in G.predecessors(node):
		print "predeces-->node: ",p,"-->",node
print
# ISOLATED NODES		
if(nx.isolates(G)):
	for node in nx.isolates(G):
		print("Isolated node ", node)
print		
for node in G.nodes():
	for p in G.predecessors(node):
		if(node == 5):
			print "Node 5 predecessor's edges: ",G.edges(p)
print
for node in G.nodes():
	for p in G.successors(node):
		if(node == 3):
			print "Node 3 successors's edges: ",p,"-->", G.edges(p)
print
print("Graph nodes: ",G.number_of_nodes())
print("Graph edges: ",G.number_of_edges())
print
node = 3
predecessors = [pred for pred in G.predecessors(node)]
print "Removing edges of node 3"
for p in predecessors:
	print "Removing ",p,"-->",node
	G.remove_edge(p,node)

print "After deletion"
print("Graph nodes: ",G.number_of_nodes())
print("Graph edges: ",G.number_of_edges())
print
print "3-->1 edge must be missing now"
for node in G.nodes():
	for p in G.predecessors(node):
		print "predeces-->node: ",p,"-->",node


#graphical representation
'''
nx.draw(G,with_labels=True)
plt.savefig("graph.png")
plt.show()
'''
								

#print(G.adj) #works ok



