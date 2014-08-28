import sys
import time
from pyndn import Name, Data, Interest, ThreadsafeFace, Exclude
from pyndn.security import KeyChain
import trollius as asyncio
import logging


class SongHandler:

    def __init__(self):
        logging.basicConfig()
        self.keychain = KeyChain()
	self.certificateName = self.keychain.getDefaultCertificateName()
	self.listPrefix = "/ndn/edu/ucla/remap/music/play"
        self.face = None
        self.loop = None
	
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
        return interest

    def issueStopCommand(self):
        stopInterest = self.createSongCommand("stop")
	self.face.expressInterest(stopInterest,self.onSongResponse,self.onSongTimeout)
        
    
    def issuePlayCommand(self):
        playInterest = self.createSongCommand("play")
	self.face.expressInterest(playInterest,self.onSongResponse,self.onSongTimeout)
          
  
    
    def onSongTimeout(self, interest):
	print "weird"

    def onSongResponse(self, interest, data):
	print("Whiling listening the music, you can do something else:")
        print("1.To pause, please type in '1'")
        print("2.To resume, please type in '2'")
	print("3.To change to another song, please type in the song name")
	
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
        self.loop = asyncio.get_event_loop()
        self.face = ThreadsafeFace(self.loop, "")
        self.face.setCommandSigningInfo(self.keychain, self.certificateName) 
        self.songName = raw_input("Song Name(each song separated by a comma): ")
	self.device = raw_input("Music Player: ")
        self.issueSongCommand()
        
        try:
            self.loop.run_forever()
        finally:
            self.stop()
        


if __name__ == '__main__':

    
      sh  = SongHandler()
      sh.start()
