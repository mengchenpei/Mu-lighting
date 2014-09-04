import sys
import time
from pyndn import Name, Data, Interest, ThreadsafeFace, Exclude,Blob
from pyndn.security import KeyChain
import trollius as asyncio
import logging
import thread,threading
songList = []
class ListRequiry:
    
    def __init__(self,skeychain,sloop,sface):
        logging.basicConfig()
        self.keychain = skeychain
        
        self.listPrefix = "/ndn/broadcast/mulighting/list"
        self.listPrefixName = Name(self.listPrefix)
        self.face = sface
        self.loop = sloop

        self.totalList = []
        #self.tempList = []

        #self.deviceList = []

        #self.listUpdate = False

    def issueListCommand(self,excludeDevice=None):
        if excludeDevice == None:
                interestName = Name(self.listPrefix)
                        
        else:
                interestName = Name(self.listPrefix).append(str("exc")+excludeDevice)

        command = Interest(interestName)
        command.setInterestLifetimeMilliseconds(4000)
        print "interestName:", interestName.toUri()
        self.face.expressInterest(command,self.onListResponse,self.onListTimeout)
        print "after send interest"
  
        

    def onListTimeout(self, interest=None):
        print "The song list has been updated!"
	print "********************Current Song List***********************"
	print self.totalList
	print "************************************************************"
        return self.totalList
        
    
    def onListResponse(self, interest, data):
        print "receive data"
        tempCont = data.getContent()
        print "temList:",tempCont
        tempStr = tempCont.__str__()
        time.sleep(1)
        tempList = tempStr.split(",")
        for i in tempList:
                self.totalList.append(i)
        print "List Update:",self.totalList
        dataName = Name(data.getName())
        deviceComponent = data.getName().get(dataName.size()-1)
        device = deviceComponent.toEscapedString()
        self.issueListCommand(device)

    def stop(self):
        self.loop.close()
        self.face.shutdown()

    def start(self):
        self.issueListCommand()
        

        #asyncio.Task(self.issueListCommand())
class SongHandler:

    def __init__(self,skeychain,sloop,sface,songList):
        logging.basicConfig()
        self.keychain = skeychain
        #self.certificateName = self.keychain.getDefaultCertificateName()
        self.listPrefix = "/ndn/edu/ucla/remap/music/play"
        self.face = sface
        self.loop = sloop

	self.songList = songList
        
        self.songName = ""
        self.device = ""

        self.inDecision = True


    def issueSongCommand(self):
        command = self.createSongCommand(self.songName)
        self.face.expressInterest(command,self.onSongResponse,self.onSongTimeout)
     

    def createSongCommand(self,command):
        interestName = Name(self.listPrefix).append(self.device)
        interestName = interestName.append(command)
        interest = Interest(interestName)
	interest.setInterestLifetimeMilliseconds(4000)
        return interest

    def issueStopCommand(self):
        stopInterest = self.createSongCommand("stop")
	stopInterest.setInterestLifetimeMilliseconds(4000)
        self.face.expressInterest(stopInterest,self.onSongResponse,self.onSongTimeout)
        
    
    def issuePlayCommand(self):
        playInterest = self.createSongCommand("play")
	playInterest.setInterestLifetimeMilliseconds(4000)
        self.face.expressInterest(playInterest,self.onSongResponse,self.onSongTimeout)
          
  
    
    def onSongTimeout(self, interest):
	print "-----------------------------------------------------"
        print "| Oops, the song is on the way, please try again... |"
	print "-----------------------------------------------------"
	self.onSongResponse(interest)

    def onSongResponse(self, interest, data=None):
	print "------------------------------------------------------------"
        print "|Whiling listening the music, you can do something else:   |"
        print "|1.To pause, please type in '1'                            |"
        print "|2.To resume, please type in '2'                           |"
        print "|3.To change to another song, please type in the song name |"
	print "------------------------------------------------------------" 

	print "********************Current Song List***********************"
	print self.songList
	print "************************************************************"
      
        cmd = raw_input(">>")
        if cmd == '1':
            self.issueStopCommand()
        if cmd == '2':
            self.issuePlayCommand()
        else:
            while True:
                    decision = raw_input("Do you want to change your music player? Y/N : ")
                    if decision == 'Y' or decision == 'y':
                        self.device = raw_input("Music Player: ")
                        break
                    if decision =='N'or decision == 'n':
                        break
                    else:
                        print "Please make sure you are typing in Y or N"                                
                        
            
            self.songName = cmd        
            self.issueSongCommand()
         
            
            
          
    def stop(self):
        self.loop.close()
        self.face.shutdown()

    def start(self):
        #self.loop = asyncio.get_event_loop()
        #self.face = ThreadsafeFace(self.loop, "")
        #self.face.setCommandSigningInfo(self.keychain, self.certificateName) 
        self.songName = raw_input("Song Name(each song separated by a comma): ")
        self.device = raw_input("Music Player: ")
        self.issueSongCommand()
    
def runForever(loop):
        try:
            loop.run_forever()
        finally:
            sys.exit()        
        
if __name__ == '__main__':

        skeychain = KeyChain()
        scertificateName = skeychain.getDefaultCertificateName()
        sloop = asyncio.get_event_loop()
        sface = ThreadsafeFace(sloop, "")
        
        sface.setCommandSigningInfo(skeychain, scertificateName) 
    
        t = threading.Thread(target = runForever, args = (sloop,))
        t.daemon = True
        t.start()
    
        #obtaining song list
        lq = ListRequiry(skeychain,sloop,sface)
        lq.start()
	songList = lq.onListTimeout()
        #wait for 15 sec
        time.sleep(10)
        #order song
        sh  = SongHandler(skeychain,sloop,sface,songList)
        sh.start()

        #print "haha"
        
        while True:
            time.sleep(10)
