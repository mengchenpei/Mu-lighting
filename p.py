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
from lighting.light_command_pb2 import LightCommandMessage
from random import randrange

from pyndn.encoding import ProtobufTlv

#try:
#    import asyncio
#except ImportError:
import trollius as asyncio
from trollius import Return, From
#script = argv #for music input


logging.getLogger('trollius').addHandler(logging.StreamHandler())



q = Queue.Queue()
#isPlaying = False
class MusicPlayer:
	isPlaying = False
        def __init__(self):
		print "dasf"

	#@staticmethod
	def play_music(self,fmusic,songList):
		print"songlist leng:",len(songList)
		if len(songList)==1 :
	    		print "enter len=1"
	    		if not MusicPlayer.isPlaying:
				print "enter playing",fmusic
				#play the music
				pygame.init()
				pygame.mixer.init()
				pygame.mixer.music.load(fmusic)
				pygame.mixer.music.play()
				MusicPlayer.isPlaying = True
	    		else:
				print "I will stop the music and play another one"
				pygame.mixer.music.stop()
				pygame.mixer.music.load(fmusic)
				pygame.mixer.music.play()
				MusicPlayer.isPlaying = True
	  	else:
			q.put(fmusic)
			pygame.init()
			pygame.mixer.init()
			if not MusicPlayer.isPlaying:
				MusicPlayer.isPlaying = True
				for i in range(0,len(songList)):
					print "enter"
					
					pygame.mixer.music.load(q.get())
					pygame.mixer.music.play()
				

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

	
	self.ftxt = ""
	self.ffreq = ""

	

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

	    config = RawConfigParser()
	    config.read('config.cfg')
	    s = LightMessenger(config)
	    
		#get the name of song
	    '''print "please type in the music you want to play:"
	    f = raw_input(">")
	    fmusic = f+str(".mp3")
	    fos = f+str("-o.txt")
	    ffreq = f+str(".txt")'''
	    	
	    print fos
	    txt = open (self.ftxt)
	    #print "open txt successfully"
	
		#collect the onset duration
	    osDur = [0.0]
	    freq = []
	    data = [float(line.split()[0])for line in txt]
	
	    for i in data:
	    	osDur.append(i)
	    txt.close()
	    txt = open (self.ffreq)
	    data = [float(line.split()[1])for line in txt]
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

    	    self.thread.start()  
	    print "enter playFunction"  
	    s.start(osDur,startingColors)

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
            	fmusic = i+str("-music.mp3") 
		self.ftxt = i + str("-o.txt")
		self.ffreq = i + str("-f.txt")
		print "FMUSIC:",fmusic 
		mp = MusicPlayer()  
	    	self.thread = threading.Thread(target = mp.play_music, args = (fmusic,songList,))
	    	self.thread.daemon = True
            	g = GetFile(self._repoCommandPrefix, i, self._face, self.playFunction)
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
    















        
