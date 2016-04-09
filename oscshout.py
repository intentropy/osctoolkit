#!/bin/python
'''
OSC Shout
  oscshout.py

    Written By: Shane Hutter
    
    Required Dependencies:  python >= 3.5, pyliblo

      This python script, and all of OSC_Tools is licensed
      under the GNU GPL version 3

      This program sends OSC Messages via the command line
'''

import liblo, sys

#program CONST
IP_PORT_PATH_ARG_INDEX=1
IP_PORT_PATH_INDEX=0
IP_INDEX=0
PORT_PATH_INDEX=1
PORT_INDEX=0
FIRST_PATH_DIR_INDEX=1
ERROR=255
CLEAN=0

#OSC CONST
LAST_OSC_ARG_INDEX=0
TOTAL_NON_OSC_ARG_INDICES=2

#osc Vars
oscPathDir=[]
oscPath=''
oscArgList=[]

def helpAndExit():
    print('Help File')
    sys.exit(CLEAN)

def sendOSC(target, path, args):
    #send osc messages in this function
    #send up to 8 arguments in a message
    if len(args)==1:
        liblo.send(target, path, args[0])
    elif len(args)==2:
        liblo.send(target, path, args[0], args[1])
    elif len(args)==3:
        liblo.send(target, path, args[0], args[1], args[2])
    elif len(args)==4:
        liblo.send(target, path, args[0], args[1], args[2], args[3])
    elif len(args)==5:
        liblo.send(target, path, args[0], args[1], args[2], args[3], args[4])
    elif len(args)==6:
        liblo.send(target, path, args[0], args[1], args[2], args[3], args[4], args[5])
    elif len(args)==7:
        liblo.send(target, path, args[0], args[1], args[2], args[3], args[4], args[5], args[6])
    elif len(args)==8:
        liblo.send(target, path, args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7])
    else:
        helpAndExit()
    return

#parse arguments
if len(sys.argv)<=2:
    helpAndExit()
else:
    try:
        #1st argument syntax: IP:Port/osc/path
        #the following arguments are based into a list (up to 8)
        #into sendOSC(target, '/osc/path', argumentList)
        oscIpPortPath=sys.argv[IP_PORT_PATH_ARG_INDEX].split()[IP_PORT_PATH_INDEX]
        oscTargetIp=oscIpPortPath.split(':')[IP_INDEX]
        oscTargetPort=int(oscIpPortPath.split(':')[PORT_PATH_INDEX].split('/')[PORT_INDEX])
        for pathDir in range(FIRST_PATH_DIR_INDEX,len(oscIpPortPath.split(':')[PORT_PATH_INDEX].split('/'))):
            oscPathDir.append(oscIpPortPath.split(':')[PORT_PATH_INDEX].split('/')[pathDir])
        for oscPathDirIndex in range(0,len(oscPathDir)):    
            oscPath+='/'+oscPathDir[oscPathDirIndex]
                
    except:
        helpAndExit()
    #grab the osc message arguments and store in list
    firstOscArgIndex=TOTAL_NON_OSC_ARG_INDICES-len(sys.argv)
    for oscArg in range(firstOscArgIndex, LAST_OSC_ARG_INDEX):
        oscArgList.append(sys.argv[oscArg])
    for oscArg in range(0,len(oscArgList)):
        try:
            #make arg an int
            oscArgList[oscArg]=int(oscArgList[oscArg])
        except:
            try:
                #make arg a float
                oscArgList[oscArg]=float(oscArgList[oscArg])
            except:
                #keep arg a string
                oscArgList[oscArg]=str(oscArgList[oscArg])
        
#create OSC Client
try:
    oscTarget=liblo.Address(oscTargetIp, oscTargetPort)
except liblo.AddressError as error:
    print(str(error))
    sys.exit(ERROR)

sendOSC(oscTarget, oscPath, oscArgList)
sys.exit(CLEAN)
