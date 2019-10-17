#!/usr/bin/python

from array import *
import serial
import time
import numpy
from collections import defaultdict
import sys
from dict_class import Mapping

nodesMap = {}
map = {}

map["george"] ={}
map["try"] ={}
map["John"] ={}

map["george"]["IP_1"] = 322
map["george"]["IP_3"] = 655
map["try"]["IP_34"] = 2
map["John"]["IP_31"] = 232
#map.__setitem__("george",nodesMap.__setitem__("IP_2",23))
#map.__setitem__("george",nodesMap.__setitem__("IP_3",655))
#map.__setitem__("try",nodesMap.__setitem__("IP_12",21))
#map.__setitem__("try",nodesMap.__setitem__("IP_34",2))
#map.__setitem__("John",nodesMap.__setitem__("IP_55",333))

counter = 0

#print(map)
#print(nodesMap)
#print(map["george"]) #prints none
#print(map.__getitem__("george")) #prints none
#for i in map:
#	print map[i].__getitem__()

#print(map.values()) #returns none!
#print(map.keys()) #returns keys ok
#print(map.items()) #returns the outer keys with NONE ONLY

for p_id, p_info in map.items():
	#print
    print("Person ID:", p_id)
    for key in p_info:
        print(key + ':', p_info[key])

del map["george"]["IP_1"]		
		

for p_id, p_info in map.items():
	#print
    print("Person ID:", p_id)
    for key in p_info:
        print(key + ':', p_info[key])