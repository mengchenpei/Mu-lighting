# THIS IS NOT USING A REPO YET
# TODO: put query interval in config

from sys import argv #for song's title input
from pyndn import Name, Data, Interest, Face, Exclude
from pyndn.security import KeyChain
from ConfigParser import RawConfigParser
from lighting.light_command_pb2 import LightCommandMessage
from random import randrange

import pygame #to play the song
import logging
import traceback
import time
import thread
import datetime
import threading

from pyndn.encoding import ProtobufTlv

#try:
#    import asyncio
#except ImportError:
import trollius as asyncio
from trollius import Return, From
script = argv #for music input


logging.getLogger('trollius').addHandler(logging.StreamHandler())

class LightMessenger:
    def __init__(self, config):

        self.keychain = KeyChain()
        self.lightAddress = config.get('lighting', 'address')

        self.lightPrefix = config.get('lighting', 'prefix')

        self.lightFace = None
        self.loop = None

        self.currentColor = (0,0,0)
	#self.transitionColor = (0,0,0)
	self.offColor = (0,0,0)
	#self.nearColor = (0,0,0)
	self.osDur=[]
	self.freq = []

        self.certificateName = self.keychain.getDefaultCertificateName()
    
        # zhehao: omg the ugliness of on/off...let's try 6 states instead
	self.commands = []
	self.transStates = 6
	#self.transValue = 1
    def unix_time_now(self):
        epoch = datetime.datetime.utcfromtimestamp(0)
        delta = datetime.datetime.utcnow() - epoch
        return delta.total_seconds() * 1000.0

  #  @asyncio.coroutine
    def issueLightingCommand(self,osDur,startingColors):

	initialColors = startingColors
	command2 = self.createLightingCommand(self.offColor)
	#command3 = self.createLightingCommand(self.nearColor)
	#aveFq = sum(freq)/len(freq)
	#s.currentColor = (5,5,8)
	
	#command = self.createLightingCommand(self.currentColor)
	#mi = min(startingColors[0],startingColors[1],startingColors[2])	
	#if mi<6:
		#startingColors = [startingColors[0]+(6-mi),startingColors[1]+(6-mi),startingColors[2]+(6-mi)]
	#mi = min(startingColors[0],startingColors[0],startingColors[2])	
	#print startingColors	
	#print "mi=",mi
	#sending Interest at every onset point

	# zhehao: generate the set of commands; we only need to do it once outside the main loop
	
	for i in range(0,self.transStates):
	
		self.currentColor = tuple(startingColors)
		#command = self.createLightingCommand(self.currentColor)
		for j in range(0,3):
			startingColors[j] -= int((initialColors[j]+self.transStates-1)/self.transStates)
			if startingColors[j]<=0:
				startingColors[j] = 0
		self.commands.append(self.createLightingCommand(self.currentColor))
		print self.currentColor
	sendTimeFile = open('interestExpressTime', 'w')
	#print len(osDur)
	for i in range(1,len(osDur)): 		
		
		print datetime.datetime.now()
		diff = osDur[i]-osDur[i-1]
		print diff/2
		if(diff>=1):
			for j in range(0,self.transStates):
				#print s.currentColor
				sendTimeFile.write('{0:f}'.format(self.unix_time_now()) + '\n')
	 			self.lightFace.expressInterest(self.commands[j], self.onLightingResponse, self.onLightingTimeout)
				time.sleep((osDur[i]-osDur[i-1])/2/self.transStates)
			sendTimeFile.write('{0:f}'.format(self.unix_time_now()) + '\n')
			self.lightFace.expressInterest(command2, self.onLightingResponse, self.onLightingTimeout)
			#print datetime.datetime.now()
			time.sleep((osDur[i]-osDur[i-1])/2)
		elif(0.5<diff<1):
			sendTimeFile.write('{0:f}'.format(self.unix_time_now()) + '\n')
			self.lightFace.expressInterest(self.commands[2], self.onLightingResponse, self.onLightingTimeout) 
			time.sleep((diff)/2)
			sendTimeFile.write('{0:f}'.format(self.unix_time_now()) + '\n')
			self.lightFace.expressInterest(self.commands[self.transStates-1], self.onLightingResponse, self.onLightingTimeout)
			#print datetime.datetime.now()
			time.sleep((osDur[i]-osDur[i-1])/2)
		elif(0.15<diff<0.5):
			sendTimeFile.write('{0:f}'.format(self.unix_time_now()) + '\n')
			self.lightFace.expressInterest(self.commands[0], self.onLightingResponse, self.onLightingTimeout) 
			time.sleep((diff)/2)
			sendTimeFile.write('{0:f}'.format(self.unix_time_now()) + '\n')
			self.lightFace.expressInterest(self.commands[self.transStates-2], self.onLightingResponse, self.onLightingTimeout)
			#print datetime.datetime.now()
			time.sleep((osDur[i]-osDur[i-1])*30/61)
		else:
			time.sleep((diff)/2)
			sendTimeFile.write('{0:f}'.format(self.unix_time_now()) + '\n')
			self.lightFace.expressInterest(command2, self.onLightingResponse, self.onLightingTimeout)
			#print datetime.datetime.now()
			time.sleep((osDur[i]-osDur[i-1])/2)
		


    def createLightingCommand(self, color):
        interestName = Name(self.lightPrefix).append('setRGB')
	print "interest prefix",self.lightPrefix,type(self.lightPrefix)
        commandParams = LightCommandMessage()
        
        messageColor = commandParams.command.pattern.colors.add()
        messageColor.r = color[0]
        messageColor.g = color[1]
        messageColor.b = color[2]

        commandName = interestName.append(ProtobufTlv.encode(commandParams))
        interest = Interest(commandName)

        return interest

    def onLightingTimeout(self, interest):
        pass

    def onLightingResponse(self, interest, data):
        #TODO: check if yhr light controller really sent this
        pass

    def stop(self):
        self.loop.close()
        self.lightFace.shutdown()

    def start(self,osDur,startingColors):
        self.loop = asyncio.get_event_loop()
        self.lightFace = Face(self.lightAddress)
        self.lightFace.setCommandSigningInfo(self.keychain, self.certificateName) 

   	
        asyncio.Task(self.issueLightingCommand(osDur,startingColors))


class MusicPlayer:
        def __init__(self):
		print "init"

	@staticmethod
	def play_music(fmusic):
		print fmusic
		#play the music
		pygame.init()
		pygame.mixer.init()
		pygame.mixer.music.load(fmusic)
		pygame.mixer.music.play()
		#print "here"
		#while pygame.mixer.music.get_busy():
		#	pygame.time.Clock().tick(10)
		#while True:
			#print "what"
			#s.face.processEvents()
			#s.issueLightingCommand()
    	#except KeyboardInterrupt:
        	#s.stop()
	

if __name__ == '__main__':
    config = RawConfigParser()
    config.read('config.cfg')
    s = LightMessenger(config)
    
	#get the name of song
    print "please type in the music you want to play:"
    f = raw_input(">")
    fmusic = f+str(".mp3")
    fos = f+str("-o.txt")
    ffreq = f+str(".txt")
    	
    print fos
    txt = open (fos)
    #print "open txt successfully"
	
	#collect the onset duration
    osDur = [0.0]
    freq = []
    data = [float(line.split()[0])for line in txt]
	
    for i in data:
    	osDur.append(i)
    txt.close()
    txt = open (ffreq)
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
    #nearColor = [int((10+r)/3), int(3), int((10+b)/3)]

    t = threading.Thread(target = MusicPlayer.play_music, args = (fmusic,))
    t.daemon = True
    t.start()
    #print "hey"
    #while True:
     #   time.sleep(50)
    #thread.start_new_thread(MusicPlayer.play_music, (fmusic,))
    s.start(osDur,startingColors)
	
