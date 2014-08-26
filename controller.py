import sys
import time
from pyndn import Name, Data, Interest, ThreadsafeFace, Exclude
from pyndn.security import KeyChain
import trollius as asyncio
import logging
from orderSong import SongHandler



class ListRequiry:
    
    def __init__(self):
	logging.basicConfig()
        self.keychain = KeyChain()
        self.certificateName = self.keychain.getDefaultCertificateName()
        listPrefix = "/ndn/edu/ucla/remap/music/list"
	self.listPrefix = Name(listPrefix)
        self.face = None
        self.loop = None

        self.totalList = []
        self.tempList = []
	self.tempString = ""

        self.deviceList = []


    def issueListCommand(self):
        command = self.creatListCommand()
        self.face.expressInterest(command,self.onListResponse,self.onListTimeout)
	print "issue /list interest",Name(command.getName()).toUri()

                
        
    def creatListCommand(self,excludeDevice=None):
        if excludeDevice == None:
            interestName = Name(self.listPrefix)
        else:
	    interestName = Name(self.listPrefix)
        interestLR = Interest(interestName)
        return interestLR

    def onListTimeout(self, interest):

	ex = self.deviceList[-1]
        command2 = self.creatListCommand(excludeDevice=ex)
        self.face.expressInterest(command2,self.onListResponse,self.onListTimeout)
	print "Send again"
        
    
    def onListResponse(self, interest, data):
	print "receive data"
        self.tempString = data.getContent().__str__()
	self.tempList = self.tempString.split(",")
	
        for i in self.tempList:
            self.totalList.append(i)
	print self.totalList

        dataName = Name(data.getName())
        deviceComponent = data.getName().get(self.listPrefix.size())
        device = deviceComponent.toEscapedString()
        self.deviceList.append(device)
	print self.deviceList
			
        ex = self.deviceList[-1]
        command2 = self.creatListCommand(excludeDevice=ex)
        self.face.expressInterest(command2,self.onListResponse,self.onListTimeout)
	print "send next interest"
	print "interetname is",Name(command2.getName()).toUri()


    def stop(self):
        self.loop.close()
        self.face.shutdown()

    def start(self):
        self.loop = asyncio.get_event_loop()
        self.face = ThreadsafeFace(self.loop,"")
        self.face.setCommandSigningInfo(self.keychain, self.certificateName) 
 	
        self.issueListCommand()
	
	try:
            self.loop.run_forever()
        finally:
            self.stop()

        
        
if __name__ == '__main__':
    
        lq = ListRequiry()
        lq.start()

	
