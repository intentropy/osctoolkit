#!/usr/bin/env python
'''
OSC Whispers
    oscwhispers.py
      Written by: Shane Huter

    Required Dependencies:  python >= 3.5, pyliblo

      This python script, and all of OSC_Tools is licensed
      under the GNU GPL version 3

      This program forwards OSC Messages.
'''

import sys, liblo

#PROGRAM CONST
CLEAN=0
ERROR=255
ENUM_ITERATE_INDEX=0
ENUM_VALUE_INDEX=1

#OSC CONST
IP_INDEX=0
PORT_INDEX=1
PATH_INFO_LIST_INDEX=0
CLIENT_TARGET_LIST_INDEX=1
PATH_PREFIX_INDEX=0
TRUNCATE_INDICATOR_INDEX=1
PATH_PREFIX_SPLIT_INDEX=1
STARTING_NON_PATH_PREFIX_INDEX=2

#program vars
forwardingList=[]
oscMessageTargets=[]
targetIdList=[]
tempMessageTargets=[]
reusedTarget=False

#OSC vars
oscTarget=[]

#Help and exit
def helpAndExit(exitStatus):
    print('Usage:')
    print('  oscwhispers [FILENAME]')
    print()
    print('Further Documentation:')
    print('  https://github.com/ShaneHutter/python-osctools/wiki')
    print()
    sys.exit(exitStatus)

if len(sys.argv)!=2:
    helpAndExit(ERROR)
    
#load config file and declare global vars
#CONFIG CONST
CONFIG_PROPERTY_ARG=0
CONFIG_VALUE_ARG=1
#config
try:
    configFileName='osctools.conf'
    configFile=open(configFileName,'r')
    configLines=configFile.read().split('\n')
except:
    configFileName='/etc/osctools.conf'
    configFile=open(configFileName,'r')
    configLines=configFile.read().split('\n')
finally:
    configFile.close()
for lineRead in configLines:
    if (lineRead!="") and (lineRead.strip().startswith('#')==False):
        #verbosity settings
        if lineRead.split()[CONFIG_PROPERTY_ARG]=='oscwhispers.verbose_listen_port':
            global verboseListenPort
            verboseListenPorts=bool(int(lineRead.split()[CONFIG_VALUE_ARG]))
        if lineRead.split()[CONFIG_PROPERTY_ARG]=='oscwhispers.verbose_incoming_osc':
            global verboseIncomingOsc
            verboseListenPorts=bool(int(lineRead.split()[CONFIG_VALUE_ARG]))
        if lineRead.split()[CONFIG_PROPERTY_ARG]=='oscwhispers.verbose_outgoing_osc':
            global verboseOutgoingOsc
            verboseListenPorts=bool(int(lineRead.split()[CONFIG_VALUE_ARG]))
        if lineRead.split()[CONFIG_PROPERTY_ARG]=='oscwhispers.verbose_forwarding_list':
            global verboseForwardingList
            verboseForwardingList=bool(int(lineRead.split()[CONFIG_VALUE_ARG]))

        #OSC Settings
        if lineRead.split()[CONFIG_PROPERTY_ARG]=='oscwhispers.listen_port':
            global listenPort
            listenPort=int(lineRead.split()[CONFIG_VALUE_ARG])

#load the forwarding destinations from file
#FILE LOAD CONST
PATH_PREFIX_FILE_INDEX=0
TRUNCATE_INDICATOR_FILE_INDEX=1
DESTINATIONS_START_INDEX=2
#file load vars
otwFileName=sys.argv[1]
otwFile=open(otwFileName, 'r')
otwLines=otwFile.read().split('\n')
otwFile.close()
for lineRead in otwLines:
    if lineRead!="" and lineRead.strip().startswith('#')==False:
        if lineRead.strip().startswith("/")==True:
            #parse forwarding destinations line
            forwardingPathPrefix=lineRead.split()[PATH_PREFIX_FILE_INDEX].strip('/')
            if lineRead.split()[TRUNCATE_INDICATOR_FILE_INDEX]=="+":
                #do not truncate prefix of path
                truncatePathPrefix=False
            elif lineRead.split()[TRUNCATE_INDICATOR_FILE_INDEX]=="-":
                #truncate prefix of path
                truncatePathPrefix=True
            else:
                helpAndExit(ERROR)
            pathPrefixInfo=[forwardingPathPrefix,truncatePathPrefix]
            for destination in range(DESTINATIONS_START_INDEX,len(lineRead.split())):
                #load the destinations into its own list, and load the index of the destination into the forwardingList
                #It will have to scan back through the destination (server list) to make sure it doesnt store duplicates
                messageIP=lineRead.split()[destination].split(':')[IP_INDEX]
                messagePort=int(lineRead.split()[destination].split(':')[PORT_INDEX])
                tempMessageTargets.append([messageIP, messagePort])
                for targetScan in enumerate(tempMessageTargets):
                    oscMessageTargets.append([targetScan[ENUM_VALUE_INDEX][IP_INDEX], targetScan[ENUM_VALUE_INDEX][PORT_INDEX]])
                    targetId=len(oscMessageTargets)-1
                targetIdList.append(targetId)
                tempMessageTargets=[]
            forwardingList.append([pathPrefixInfo, targetIdList])
            reusedTarget=False
            targetIdList=[]
            
#setup OSC Server
try:
    oscListenServer=liblo.Server(listenPort)
except liblo.ServerError as error:
    print(str(error))
    sys.exit(ERROR)

#setup OSC clients
for target in enumerate(oscMessageTargets):
    print(target[ENUM_ITERATE_INDEX])
    print(target[ENUM_VALUE_INDEX][IP_INDEX], target[ENUM_VALUE_INDEX][PORT_INDEX])
    try:
        oscTarget.append(liblo.Address(target[ENUM_VALUE_INDEX][IP_INDEX], target[ENUM_VALUE_INDEX][PORT_INDEX]))
    except liblo.AddressError as error:
        print(str(error))
        sys.exit(ERROR)

def sendOSC(target, path, args):
    #send osc messages in this function
    libloSend='liblo.send(target, path'
    for eachArg in range(0,len(args)):
        libloSend+=', args['+str(eachArg)+']'
    libloSend+=')'
    exec(libloSend)
    return

def truncatePathPrefix(inpath):
    #truncate osc paths here
    outpath=''
    for dirs in range(STARTING_NON_PATH_PREFIX_INDEX,len(inpath.split('/'))):
        outpath+='/'+inpath.split('/')[dirs]
    return outpath

def pathPrefix(inpath):
    #this function returns the a paths top level
    prefix=inpath.split('/')[PATH_PREFIX_SPLIT_INDEX]
    return prefix

def forwardMessage(path, args):
    for eachList in range(0,len(forwardingList)):
        if forwardingList[eachList][PATH_INFO_LIST_INDEX][PATH_PREFIX_INDEX]==pathPrefix(path):
            if forwardingList[eachList][PATH_INFO_LIST_INDEX][TRUNCATE_INDICATOR_INDEX]==True:
                for eachTarget in range(0,len(forwardingList[eachList][CLIENT_TARGET_LIST_INDEX])):
                    sendOSC(oscTarget[forwardingList[eachList][CLIENT_TARGET_LIST_INDEX][eachTarget]], truncatePathPrefix(path), args)
            else:
                for eachTarget in range(0,len(forwardingList[eachList][CLIENT_TARGET_LIST_INDEX])):
                    sendOSC(oscTarget[forwardingList[eachList][CLIENT_TARGET_LIST_INDEX][eachTarget]], path, args)
    return
        
#register OSC Listen method
oscListenServer.add_method(None, None, forwardMessage)
    
#output Startup verbosity
if verboseForwardingList==True:
    print()
    for eachList in range(0,len(forwardingList)):
        #make this output look nicer
        print('Path with prefix /', end='')
        print(forwardingList[eachList][PATH_INFO_LIST_INDEX][PATH_PREFIX_INDEX], end=' ')
        if forwardingList[eachList][PATH_INFO_LIST_INDEX][TRUNCATE_INDICATOR_INDEX]==True:
            print('will truncate path prefix.')
        else:
            print('will not truncate path prefix.')
        print('Then it will forward to:')
        for target in range(0,len(forwardingList[eachList][CLIENT_TARGET_LIST_INDEX])):
            print('IP: ', end='')
            print(oscMessageTargets[forwardingList[eachList][CLIENT_TARGET_LIST_INDEX][target]][IP_INDEX], end='    Port: ')
            print(str(oscMessageTargets[forwardingList[eachList][CLIENT_TARGET_LIST_INDEX][target]][PORT_INDEX]))
        print()

#main loop
while True:
    oscListenServer.recv(1)
sys.exit(CLEAN)
