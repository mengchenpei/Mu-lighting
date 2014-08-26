#!/usr/bin/env python
#coding=utf-8

# Put file into repo-ng in Python, following repo protocol:
# http://redmine.named-data.net/projects/repo-ng/wiki
# Under testing: unversioned segmented data writing completed
#
# code by Mengchen, Zhehao
# Aug 21, 2014
#

import sys
import time
import trollius as asyncio
import logging

from pyndn import Name, Data, Interest, ThreadsafeFace, Exclude, Blob
from pyndn.security import KeyChain

class GetFile:

    def __init__(self, repoCommandPrefix, dataName, songHandlerFace, playFunction):
        self._repoCommandPrefix = Name("ndn:/example/repo/1")       
        self._dataName = Name(dataName)
	self.txtName = dataName + str("-o")
	self.freqName = dataName + str("-f")
	self._txtName = Name(self.txtName)
	self._freqName = Name(self.freqName) 

        self._interestLifetime = 1000
        self.m_timeout = 100
        self.m_nextSegment=0
        self.m_totalSize=0
        self.m_retryCount=0

        self.m_mustBeFresh = False

        self._face = songHandlerFace
        #self._loop = None
        
        self._keyChain = KeyChain()
        self._certificateName = self._keyChain.getDefaultCertificateName()
        
        self.oStream = None
        self._writtenSegment = 0
	self._playFunction = playFunction
        
    # Just for appending segment number 0, making it encoded as %00%00, instead of %00 in PyNDN.
    # Potential bug/loss of interoperability?
    @staticmethod
    def componentFromSingleDigitNumberWithMarkerCXX(number, marker):
        value = []
        value.append(number & 0xFF)
        number >>= 8
        value.reverse()
        value.insert(0, marker)
        return Name.Component(Blob(value, False))

    def start(self):
        #self._loop = asyncio.get_event_loop()
        #self._face = ThreadsafeFace(self._loop,"")
        #self._face.setCommandSigningInfo(self._keyChain, self._certificateName)
        
        zero = GetFile.componentFromSingleDigitNumberWithMarkerCXX(0, 0x00)
        
        self.startFetchingData(Name(self._dataName).append(zero))
	#self.startFetchingData(Name(self._txtName).append(zero))
        
        #try:
         #   self._loop.run_forever()        
        #finally:
            #self.stop()
          
    def stop(self):
        #self._loop.close()         
        #self._face.shutdown()
        #self._face = None
        sys.exit(1)

    def startFetchingData(self,name):
        interest = Interest(name)
        interest.setInterestLifetimeMilliseconds(self._interestLifetime)
        interest.setMustBeFresh(self.m_mustBeFresh)
        
        self._face.expressInterest(interest, self.onFirstData, self.onTimeout)
        

    def fetchData(self,name):
        interest = Interest(name)
        interest.setInterestLifetimeMilliseconds(self._interestLifetime)
        interest.setMustBeFresh(self.m_mustBeFresh)
        
        self._face.expressInterest(interest,self.onData,self.onTimeout)
        
    def onData(self,interest,data):
        print "receive data from repo"
        dataName = data.getName()
        print dataName.toUri()
        
        if(dataName.size() != self._dataName.size() + 1):
            print dataName.size(),self._dataName.size()+1
            raise Exception("unexpected data name size.")
        segment = dataName[-1].toSegment()

        content = data.getContent()
        
        # Write the correct segment; if segments arrive in wrong order, let the user know
        if self._writtenSegment + 1 == segment:
            self.oStream.write(content.toBuffer())
            self._writtenSegment += 1
        else:
            print "Segment arrived in wrong order."
        self.m_totalSize += content.size()
        
        # finalBlockId does not work well with repo-ng for now
        finalBlockId = data.getMetaInfo().getFinalBlockID()
        
        # These comparisons are apparently wrong
        print "finalBlockID,Name[-1]",finalBlockId.toEscapedString(), dataName[-1].toSegment()
        if (finalBlockId == dataName[-1].toSegment()):
            # Reach EOF
            print "INFO: End of file is reached."
            print "INFO: Total",(self.m_nextSegment - 1)," of segments received"
            print "INFO: Total",(self.m_totalSize)," bytes of content received"

        else:
            #Reset retry counter
            self.m_retryCount = 0
            #Fetch next segment
            self.m_nextSegment += 1
            self.fetchData(Name(self._dataName).appendSegment(self.m_nextSegment))
            
    #In PyNDN the first interest's name has a different segment number with other(First:%00,others:%00%xx)            
    def onFirstData(self,interest,data):
        print "receive first data from repo"
        dataName = data.getName()
        if(dataName.size() != self._dataName.size() + 1):
            raise Exception("unexpected data name size.")
        
        content = data.getContent()
        self.oStream.write(content.toBuffer())
        
        self.m_totalSize += content.size()
        
        finalBlockId = data.getMetaInfo().getFinalBlockID()
        
        print "finalBlockID,Name[-1]",finalBlockId.toEscapedString(), dataName[-1].toSegment()
        if (finalBlockId == dataName[-1].toSegment()):
            # Reach EOF
            print "INFO: End of file is reached."
            print "INFO: Total",(self.m_nextSegment - 1)," of segments received"
            print "INFO: Total",(self.m_totalSize)," bytes of content received"

        else:
            #Reset retry counter
            self.m_retryCount = 0
            self.m_nextSegment += 1
        
        # fetch regular data after receiving the first segment
        self.fetchData(Name(self._dataName).appendSegment(self.m_nextSegment))
        
    def onTimeout(self,interest):
        MAX_RETRY = 3  
        self.m_retryCount += 1
        if(self.m_retryCount <= MAX_RETRY):
            self.fetchData(interest.getName())
            print"TIMEOUT: retransmit interest..."
        else:
            print "TIMEOUT: last interest sent for segment",(self.m_nextSegment - 1)
            print "TIMEOUT: abort fetching after",(MAX_RETRY),"times of retry"
            # Probably want to close file after it finished writing
            self.oStream.close()
	    self.startFetchingData(Name(self._txtName).append(zero))
	    self.startFetchingData(Name(self._freqName).append(zero))
	    self._playFunction()
	 
    	    

if __name__ == '__main__':
    logging.basicConfig()
    #songList = ['Hotel California', 'river flows in you', 'simple way', 'star', 'mozart', 'yellow', 'canon', 'a comm amour', 'RICHA', 'merry christmas', 'love story', 'juliet', 'geqian', 'nocturne', 'RICHA1111', 'canon1', 'nocturne1', 'house_lo', 'house_lo']
    #for i in songList:
    dataName = "/example/data/1/PC35"
    repoCommandPrefix = "/example/repo/1"
    g = GetFile(repoCommandPrefix, dataName)
    
    musicOutputFile = "PC3-received.txt"
    g.oStream = open(musicOutputFile, 'wb')
    g.start()
