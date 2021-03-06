import sys
import time
from pyndn import Name, Data, Interest, ThreadsafeFace, Exclude,Blob, Sha256WithRsaSignature
from pyndn.security import KeyChain
import trollius as asyncio
import logging
import thread, threading
from pyGetFile import GetFile
from LightMessengerzhreduce import LightMessenger
import pygame
import Queue

from ConfigParser import RawConfigParser

from random import randrange

from pyndn.encoding import ProtobufTlv

#try:
#    import asyncio
#except ImportError:
import trollius as asyncio
from trollius import Return, From
#script = argv #for music input


logging.getLogger('trollius').addHandler(logging.StreamHandler())




#isPlaying = False
class MusicPlayer:
	isPlaying = False
	
        def __init__(self):
		print "dasf"
		
		pygame.init()
		pygame.mixer.init()
		

	#@staticmethod
	def play_music(self,fmusic,songList,queue):
		print"songlist leng:",len(songList)
	
		if len(songList) == 1 :
	    		print "enter len=1"
	    		if not MusicPlayer.isPlaying:
				print "enter playing",fmusic
				#play the music
				MusicPlayer.isPlaying = True
				pygame.mixer.music.load(fmusic)
				pygame.mixer.music.play()
				MusicPlayer.isPlaying = False
	    		else:
				print "I will stop the music and play another one"
				pygame.mixer.music.stop()
				MusicPlayer.isPlaying = True
				pygame.mixer.music.load(fmusic)
				pygame.mixer.music.play()
				MusicPlayer.isPlaying = False
	  	if len(songList) > 1 :
			print "enter songlist>1"
			
			if not MusicPlayer.isPlaying:
				print "multi-songs start playing"
				MusicPlayer.isPlaying = True
				print "queue:",queue
				while not queue.empty():
					i = queue.get()
					print "start play one song of multisongs"
					print "len(songList)",len(songList)
					
					print "get():",i						
					pygame.mixer.music.load(i)
					pygame.mixer.music.play()
					pygame.mixer.music.stop()
				MusicPlayer.isPlaying = False
				

class SongHandler:

    def __init__(self):

        self._device = "PC1"
        self._playPrefix = Name("/ndn/edu/ucla/remap/music/play")
	self.prefix = self._playPrefix.append(self._device)
        self._face = None
        self._loop = None

	self.thread = None
        
        self._keyChain = KeyChain()
        self._certificateName = self._keyChain.getDefaultCertificateName()

        self._repoCommandPrefix = "/example/repo/1"

	self.song = ""
	self.ftxt = ""
	self.ffreq = ""

	self.songList = ""
	self.mp = MusicPlayer()
	self.config = RawConfigParser()
	self.config.read('config.cfg')
	self.s = LightMessenger(self.config)

	self.q = Queue.Queue()
	

    def start(self):
        self._loop = asyncio.get_event_loop()
        self._face = ThreadsafeFace(self._loop,"")
        self._face.setCommandSigningInfo(self._keyChain, self._certificateName)
        self._face.registerPrefix(self.prefix, self.onPlayingCommand, self.onRegisterFailed)
	print "after register prefix"
        try:
            self._loop.run_forever()
        except KeyboardInterrupt:
            sys.exit()
        finally:
            self.stop()

    def stop(self):
        self._loop.close()        
        self._face.shutdown()
        sys.exit(1)

    def playFunction(self):

	    txt = open(self.ftxt)
	    print "open txt successfully",self.ftxt
	
		#collect the onset duration
	    osDur = [0.0]
	    freq = []
	    data = [float(line.split()[0])for line in txt]
	
	    for i in data:
	    	osDur.append(i)
	    txt.close()
	    txt = open(self.ffreq)
	    print "open txt successfully",self.ffreq
	    data = [float(line.split()[1])for line in txt]
	    print "dasfdaaaa"
	    for j in data:
		freq.append(j)
	    avefq = int(sum(freq)/len(freq))  
	    print avefq  	
	    txt.close()
	    g=(avefq-100)/10
	    r=avefq/30
	    b=(100-avefq)/10
	    startingColors = [int((15+r)/1.5),int((10+g)/1.5), int((10+b)/1.5)]
	    for i in range(0,3):
		if startingColors[i]<0:
			startingColors[i]=6
	    #startingColors = [5,5,5]
	    self.q.put(self.song+str("-music.mp3") )
	    print "MusicPlayer.isPlaying",MusicPlayer.isPlaying
	    if not MusicPlayer.isPlaying:
    	    	self.thread.start() 
		#MusicPlayer.isPlaying = True 
	      
	    self.s.start(osDur,startingColors)

    def getOnset(self):
	print "getonset"
	otxt = self.song+str("-o")
	print otxt
	g = GetFile(self._repoCommandPrefix, otxt, self._face, self.getFreq)
	g.oStream = open(self.song+str("-os.txt"),'wb')    
	g.start()

    def getFreq(self):
	print "getfreq"
	ftxt = self.song+str("-f")
	g = GetFile(self._repoCommandPrefix, ftxt, self._face, self.playFunction)
	g.oStream = open(self.song+str("-freq.txt"),'wb')    
	g.start()

    def signData(self, data):
        data.setSignature(Sha256WithRsaSignature())
        

    def onPlayingCommand(self, prefix, interest, transport, prefixId):
	print "receive interest"
        interestName = Name(interest.getName())
        commandComponent = interest.getName().get(self.prefix.size())
        if commandComponent == Name.Component("stop"):
            pass
        if commandComponent == Name.Component("play"):
            pass
        else:
            songName = commandComponent.toEscapedString()
	    print songName
	    songList = []
	    songList = songName.split('%2C')
	    print "songlist and its len",songList,len(songList)
	    for i in songList:
		self.song = i
            	fmusic = i+str("-music.mp3") 
		self.ftxt = i + str("-os.txt")
		self.ffreq = i + str("-freq.txt")
		print "FMUSIC:",fmusic 
		  
	    	self.thread = threading.Thread(target = self.mp.play_music, args = (fmusic,songList,self.q,))
	    	self.thread.daemon = True
            	g = GetFile(self._repoCommandPrefix, i, self._face, self.getOnset)
		#g = GetFile(self._repoCommandPrefix, ftxt, self._face, self.lightFunction)
            	g.oStream = open(fmusic,'wb')
            	g.start()
	   
		
	
	d = Data(interest.getName())
	d.setContent("start to play: " + songName + "\n")
	encodedData = d.wireEncode()
	transport.send(encodedData.toBuffer())	

        
            
    def onRegisterFailed(self, prefix):
        self.log.error("Could not register " + prefix.toUri())
        self.stop()

if __name__ == '__main__':

	logging.basicConfig()
        sh = SongHandler()
        sh.start()
    















        
