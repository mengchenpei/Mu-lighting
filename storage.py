from pyPutFile import ThreadsafeFaceWrapper,PutFile

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

currentList=[]


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
    logging.basicConfig()
    #get the initial version of song list
    alist = CheckList.scan_files("/home/bupt/ndn-test/mu-lighting/music-file",fpostfix=".mp3")
    #oldList = []
    for p in alist:
    	s = p[:-4]  
    	currentList.append(s)
    print currentList

 
    #put the local file(music data, onset data and frequency data) to repo
    faceWrapper = ThreadsafeFaceWrapper()
    for i in currentList:
	musicFile = i+str(".mp3")
	p = PutFile(Name(i), Name("ndn:/example/repo/1"), faceWrapper.getFace(), faceWrapper.getLoop())
    	p.insertStream = open(str("music-file/")+musicFile, 'rb')
    	p.fileSize = os.stat(str("music-file/")+musicFile).st_size    
    	p.start()
	
	

	osFile = i+str("-o.txt")
	of = PutFile(Name(i+str("-o")), Name("ndn:/example/repo/1"), faceWrapper.getFace(), faceWrapper.getLoop())
    	of.insertStream = open(str("music-file/")+osFile, 'rb')
    	of.fileSize = os.stat(str("music-file/")+osFile).st_size    
    	of.start()

	freqFile = i+str(".txt")
	fq = PutFile(Name(i+str("-f")), Name("ndn:/example/repo/1"), faceWrapper.getFace(), faceWrapper.getLoop())
    	fq.insertStream = open(str("music-file/")+freqFile, 'rb')
    	fq.fileSize = os.stat(str("music-file/")+freqFile).st_size    
    	fq.start()



	
    #keep updating the temporary list
    #t = threading.Thread(target = CheckList.list_check(currentList), args = (currentList,))
    #t.daemon = True
    #t.start()

	 # Always call this when everything else is done, since it blocks in run_forever
    faceWrapper.startProcessing()
