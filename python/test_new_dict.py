#!/usr/bin/python

from nested_dict import NodesMatrix

nodesM = NodesMatrix()

#nodesM.add("George")
#nodesM.add("Tryf")


nodesM.addRec("George", "IP_1", 345)
nodesM.addRec("George", "IP_2", 32)
nodesM.addRec("Tryf", "IP_3", 22)
nodesM.addRec("Tryf", "IP_4", 67)
nodesM.addRec("Tryf", "IP_5", 9)
nodesM.addRec("John", "IP_6", 12)

#print nodesM.childValue("George", "IP_1") #ok
#print nodesM.printAllChildren("George") #ok

#for i in nodesM:
#	print nodesM
	
#print( nodesM.getNodesChildren("George")) #ok
#print( nodesM.getNodesChildren("Tryf")) #ok

#print nodesM.getAll()

#print nodesM.__getAll__()

#print nodesM.items()
print nodesM.items()
#nodesM.popChild("George","IP_1")
nodesM.addRec("Tryf", "IP_3", 432)
print nodesM.items()
#nodesM.updateChild("George","IP_2",433)
#print nodesM.items()