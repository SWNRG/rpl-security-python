#!/usr/bin/python

# Nested dictionary class.
# 
import logging

class NodesMatrix(dict):
	#def __init__(self):
	#	self.log = logging.getLogger('NodesMatrix')
	
	def add(self, node):
		self.__dict__[node] = {}
	
	def __getAll__(self):
		return self.__dict__

	def addRec(self, node):
		if not self.__contains__(node):
			self.__dict__[node] = {}

	def addRec(self, node, child):
		if not self.__contains__(node):
			self.__dict__[node] = {}
		self.__dict__[node][child]# = value
		print("New nbr added to sink")
		
		
	def addRec(self, node, child, value):
		if not self.__contains__(node):
			self.__dict__[node] = {}
			print("New node added")
		self.__dict__[node][child] = value

	def getNodesChildren(self,node):
		return self.__dict__[node]
		
	def childValue(self, node, child):
		return self.__dict__[node][child]
		
	def items(self):
		return self.__dict__.items()		
		
	def printAllChildren(self, node):
		for i in self.__dict__[node]:
			print(i, self.getChild(node, i))
			#return self.getChild(node, i)

	def pop(self, *args):
		return self.__dict__.pop(*args)
	
	def popChild(self, node, child):
		del self.__dict__[node][child]
		return self.__dict__

	def updateChild(self, node, child, value):
		self.__dict__[node][child] = value

	def keys(self):
		return self.__dict__.keys()		
	
	def values(self):
		return self.__dict__.values()

	def __contains__(self, item):
		return item in self.__dict__