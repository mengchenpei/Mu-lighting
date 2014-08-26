import sys
import time
from pyndn import Name, Data, Interest, ThreadsafeFace, Exclude
from pyndn.security import KeyChain
import trollius as asyncio
import logging

class ListRequiry:
    
    def __init__(self):
        logging.basicConfig()
        self.keychain = KeyChain()
        self.certificateName = self.keychain.getDefaultCertificateName()
        self.listPrefix = "/ndn/edu/ucla/remap/mu/list"

        self.face = None
        self.loop = None

        self.totalList = []
        self.tempList = []

        self.deviceList = []

        self.listUpdate = False

    def issueListCommand(self):
        command = self.creatListCommand()
        self.face.expressInterest(command,self.onListResponse,self.onListTimeout)
        print "issue /list interest"
        
        
                
        
    def creatListCommand(self,excludeDevice=None):
        if excludeDevice == None:
            interestName = Name(self.listPrefix)
        else:
            interestName = Name(self.listPrefix).append(excludeDevice)
        interestLR = Interest(interestName)
        return interestLR

    def onListTimeout(self, interest):
	print "weird"
        

    
    def onListResponse(self, interest, data):
        print "receive data"
        self.tempList = data.getContent()
        print self.tempList
        
        '''for i in self.tempList:
            self.totalList.append(i)
	print self.totalList
        dataName = Name(data.getName())
        deviceComponent = data.getName().get(self.listPrefix.size())
        device = deviceComponent.toEscapedString()
        deviceList.append(device)
        self.listUpdate = True'''

    def stop(self):
        self.loop.close()
        self.face.shutdown()

    def start(self):
        self.loop = asyncio.get_event_loop()
        self.face = ThreadsafeFace(self.loop, "")
        self.face.setCommandSigningInfo(self.keychain, self.certificateName) 
        self.issueListCommand()
        
        try:
            self.loop.run_forever()
        finally:
            self.stop()
        #asyncio.Task(self.issueListCommand())
        
        
if __name__ == '__main__':
    
        lq = ListRequiry()
        lq.start()
        time.sleep(600)