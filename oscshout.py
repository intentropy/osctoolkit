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

def helpAndExit(exitStatus):
    print('Help File')
    sys.exit(exitStatus)

def sendOSC(target, path, args):
    #send osc messages in this function
    libloSend='liblo.send(target, path'
    for eachArg in range(0,len(args)):
        libloSend+=', args['+str(eachArg)+']'
    libloSend+=')'
    exec(libloSend)
    return

#parse arguments
if len(sys.argv)<=2:
    helpAndExit(ERROR)
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
        helpAndExit(ERROR)
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
