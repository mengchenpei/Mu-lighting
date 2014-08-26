#!/usr/bin/env python
#coding=utf-8
import sys 
import os
import thread
import threading
import time
import logging

from pyndn import Name,Interest,ThreadsafeFace,Sha256WithRsaSignature
from pyndn import Data
from pyndn import Face
from pyndn.security import KeyChain
import trollius as asyncio

#storage devices inform their exist to network, then when controller want the songList, the interest will be broadcast to all the storage devices 

currentList=[]
class RegisterSongList(object):


    def __init__(self, prefix="/ndn/edu/ucla/remap/music/list"):

	logging.basicConfig()        
	'''#这些log是干嘛的myIP="192.168.1.1",lightIP="192.168.1.50",
        self.log = logging.getLogger("RegisterSongList")
        self.log.setLevel(logging.DEBUG)
        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        self.log.addHandler(sh)
        fh = logging.FileHandler("RegisterSongList.log")
        fh.setLevel(logging.INFO)
        self.log.addHandler(fh)'''
    	self.device = "PC3"
    	self.deviceComponent = Name.Component(self.device)
	self.excludeDevice = None
    	#self.songList = originalList

        #security?
        self.prefix = Name(prefix)
	self.changePrefix = Name("/ndn/edu/ucla/remap/music/storage")
        self.keychain = KeyChain()
        self.certificateName = self.keychain.getDefaultCertificateName()

        self.address = ""
        self._isStopped = True
  
        #self.payloadBuffer = []

        #self.kinetsender = KinetSender(myIP, playerIP,self.STRAND_SIZE*self.COLORS_PER_LIGHT)




    
    def start(self):
	print "reg start"
	self.loop = asyncio.get_event_loop()
	self.face = ThreadsafeFace(self.loop,self.address)
	self.face.setCommandSigningInfo(self.keychain,self.certificateName)
        self.face.registerPrefix(self.prefix,self.onInterest,self.onRegisterFailed)
        self._isStopped = False
        self.face.stopWhen(lambda:self._isStopped)
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:

            sys.exit()
        finally:
            self.stop()


    def stop(self):
        self.loop.close()
        #self.kinetsender.stop = True
        #self.kinetsender.complete.wait()         
        self.face.shutdown()
        self.face = None
        sys.exit(1)

    def signData(self,data):
	data.setSignature(Sha256WithRsaSignature())
	#self.keychain.sign(data,self.certificateName)

    def onInterest(self, prefix, interest, transport, registeredPrefixId):
	print "received interest"
        initInterest = Name(interest.getName())
        print "interest name:",initInterest.toUri()
        #d = Data(interest.getName().getPrefix(prefix.size()+1))
        #self.excludeDevice = interest.getName().get(prefix.size())
	#initInterest = interest.getName()
	d = Data(interest.getName().append(self.deviceComponent))
	try:
		print "start to set data's content"
                
		currentString = ','.join(currentList)
		d.setContent("songList of " +self.device+":"+currentString+ "\n")
		self.face.registerPrefix(self.changePrefix,self.onInterest,self.onRegisterFailed)	



	    

	except KeyboardInterrupt:
		print "key interrupt"
		sys.exit(1)
	except Exception as e:
		print e
		d.setContent("Bad command\n")
	finally:
		self.keychain.sign(d,self.certificateName)

	encodedData = d.wireEncode()
	transport.send(encodedData.toBuffer())
	print d.getName().toUri()
	print d.getContent()

	self.stop()
		
	'''print"remove register"
        self.face.removeRegisteredPrefix(registeredPrefixId)
        time.sleep(30)
        #sleep 30s which means user cannot update the song list twice within 1 minutes
	print"register again"
        self.face.registerPrefix(self.prefix, self.onInterest, self.onRegisterFailed)'''

    def onRegisterFailed(self, prefix):
        self.log.error("Could not register " + prefix.toUri())
        self.stop()

class CheckList(object):

    #def __init__(self):
    listDelete = []
    listAdd = []
    @staticmethod
    def scan_files(directory,fprefix=None,fpostfix=None):
        files_list=[]
     
        for root, sub_dirs, files in os.walk(directory):
            for special_file in files:
                if fpostfix:
                    if special_file.endswith(fpostfix):
                        files_list.append(os.path.join(special_file))
                elif fprefix:
                    if special_file.startswith(fprefix):
                        files_list.append(os.path.join(special_file))
                else:
                    files_list.append(os.path.join(special_file))
                           
        return files_list
   
    @staticmethod
    def list_check(currentList):
        setA=set(currentList)
        while True:
        	alist = CheckList.scan_files("/home/bupt/ndn-test/",fpostfix=".mp3")
        	tempList =[] 
        	for p in alist:
            		s = p[:-4]  
            		tempList.append(s)
        	setB = set(tempList)
       		listDelete = setA.difference(setB)
        	listAdd = setB.difference(setA)
		currentList = tempList
        	time.sleep(600)


        
if __name__ == '__main__':

    # The default Face will connect using a Unix socket, or to "localhost".
    #face = Face()

    #get the initial version of song list
    alist = CheckList.scan_files("/home/bupt/ndn-test/music/",fpostfix=".mp3")
    #oldList = [] 
    for p in alist:
	s = p[:-4]  
        currentList.append(s)
    print currentList

    print "before initial reg"
    reg = RegisterSongList(prefix="/ndn/edu/ucla/remap/music/list")
    #prefix1 = Name("/ndn/music/list")
    
    reg.start()

    #while True:
	#time.sleep(10)

    #keep updating the temporary list
    t = threading.Thread(target = CheckList.list_check(currentList), args = (currentList,))
    t.daemon = True
    t.start()

    #time.sleep(600)

     
