#!/usr/bin/python

#be carefull: if there is no pts port avaliable, it will return null. No exceptions thrown

import socket
from random import randint

address = "localhost"
port = 6100

#returns an array of ALL available pty ports (all motes...)
def getAllpts():
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.settimeout(3.0)
		sock.connect((address, port))
		f=sock.makefile()
		d=[]
		for l in f.read().split('\n'):
			d.append(l)
		sock.close()
		return d
	except Exception as e:
		print("pts server error ",e)

#returns a random EXISTING pty port of a mote...
def getRandpts():
    ptsArray=getAllpts()
    rnd=randint(0,len(ptsArray))
    return ptsArray[rnd]

#returns the 1st pty port of a mote (smallest in increasing number...)  
def get1stpts():
	try:
		ptsArray=getAllpts()
		if ptsArray:
			return ptsArray[0]
	except Exception as e:
		print("No pts port (no cooja?) found...")
		pass

#returns the 1st pty port of a mote (smallest in increasing number...)  
def getSpecificpts(pos):
    ptsArray=getAllpts()
    if pos > ptsArray[-1]:
        print ("list out of bounds. There are not so many avaliable pts ports")
        exit()
    else:
        return ptsArray[pos]
    

#if __name__ == '__main__':
#	print (getAllpty())

