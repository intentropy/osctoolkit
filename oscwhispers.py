#!/usr/bin/env python
'''
OSC Whispers
    oscwhispers.py
      Written by: Shane Huter

    Required Dependencies:  python >= 3.5, pyliblo

      This python script, and all of OSC_Tools is licensed
      under the GNU GPL version 3.

      OSC Whispers recieves OSC Messages and forwards the message to a new
      location(s) based on the messages Path Prefix.

      OSC Whispers is a part of osctoolkit.

      osctoolkit is free software; you can redistribute it and/or modify
      it under the terms of the GNU Lesser General Public License as published 
      by the Free Software Foundation, either version 3 of the License, or
      (at your option) any later version.

      osctoolkit is distributed in the hope that it will be useful,
      but WITHOUT ANY WARRANTY; without even the implied warranty of
      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
      GNU Lesser General Public License for more details.

      You should have received a copy of the GNU Lesser General Public License
      along with this program. If not, see <http://www.gnu.org/licenses/>..
'''

## Import modules
from argparse import ArgumentParser
from liblo import Address, AddressError, send, Server, ServerError
from sys import exit
from os.path import isfile


'''
ToDo:
    * Add a command and control OSC Server for issuing commands to oscwhipsers using OSC messages
    * Add an OSC Client to send debug information out as a OSC Message
        Message could be things like a "read to go" message, "shutting down" message,
        and maybe errors, etc...
    * Add logging
    * Input and output verbosity doesn't appear to be implemented
    * Use a class for configuration file parsing
'''


#PROGRAM CONST
CLEAN = 0
ERROR = 65535
ENUMERATE_ITERATE_INDEX = 0
OTW_FILE_ARG = 1
MAIN_LOOP_LATENCY = 1
MAIN_LOOP_LATENCY = 1

### Create classes
#OSC CONST
IP_INDEX = 0
PORT_INDEX = 1
PATH_INFO_LIST_INDEX = 0
CLIENT_TARGET_LIST_INDEX = 1
PATH_PREFIX_INDEX = 0
TRUNCATE_INDICATOR_INDEX = 1
PATH_PREFIX_SPLIT_INDEX = 1
STARTING_NON_PATH_PREFIX_INDEX = 2

#program vars
forwardingList = []
oscMessageTargets = []
targetIdList = []
tempMessageTargets = []
reusedTarget = False

#OSC vars
oscTarget = []


## Load config file and parse arguments
if __name__ == '__main__':
    # Configuration file contants
    CONFIG_PROPERTY_ARG = 0
    CONFIG_VALUE_ARG = 1
    CONFIG_PROTO_COMMENT = OTW_PROTO_COMMENT = 0
    CONFIG_COMMENT_SYMBOL = OTW_COMMENT_SYMBOL = '#'
    CONFIG_FILE_LOCATIONS = ['osctoolkit.conf', 
            '/home/$USER/.config/osctoolkit.conf', 
            '/etc/osctoolkit.conf']
   
    # Declare global config variables with default values
    # globals
    global verboseListenPort
    global verboseIncomingOsc
    global verboseOutgoingOsc
    global verboseForwardingList
    global verboseCommandPort
    global listenPort
    # defaults
    verboseListenPort = False
    verboseIncomingOsc = False
    verboseOutgoingOsc = False
    verboseForwardingList = False
    verboseCommandPort = False
    listenPort = 9000

    ## Load config files
    for checkConf in CONFIG_FILE_LOCATIONS:
        if isfile(checkConf):
            configFileLocation = checkConf
            break
    configFile = open(configFileLocation, 'r')
    configLines = configFile.read().split('\n')
    configFile.close()

    # Parse config file lines
    for lineRead in configLines:
        # if lineRead != '' and lineRead.strip().startswith('#')==False:
        if lineRead:
            lineReadProtoComment = lineRead.split(CONFIG_COMMENT_SYMBOL)[CONFIG_PROTO_COMMENT].split(' ')
            # Verbosity settings
            if lineReadProtoComment[CONFIG_PROPERTY_ARG] == 'oscwhispers.verbose_listen_port':
                verboseListenPort = bool(int(lineReadProtoComment[CONFIG_VALUE_ARG]))

            # add verbose command port for displaying oscwhipsers command and control port number
            
            if lineReadProtoComment[CONFIG_PROPERTY_ARG] == 'oscwhispers.verbose_incoming_osc':
                verboseIncomingOsc = bool(int(lineReadProtoComment[CONFIG_VALUE_ARG]))
            
            if lineReadProtoComment[CONFIG_PROPERTY_ARG] == 'oscwhispers.verbose_outgoing_osc':
                verboseOutgoingOsc = bool(int(lineReadProtoComment[CONFIG_VALUE_ARG]))
            
            if lineReadProtoComment[CONFIG_PROPERTY_ARG] == 'oscwhispers.verbose_forwarding_list':
                verboseForwardingList = bool(int(lineReadProtoComment[CONFIG_VALUE_ARG]))

    
            # OSC Settings
            if lineReadProtoComment[CONFIG_PROPERTY_ARG] == 'oscwhispers.listen_port':
                listenPort = int(lineReadProtoComment[CONFIG_VALUE_ARG])

    ## Parse Arguments
    '''
        Argument Notes:
            OTW Files:
            To specify otw files pass
                -f or --files
            
            Verbose:
            There are several types of verbosity that can be turned on:

            -v is global verbosity, this switchy will turn on all verbosity, regardless
                of configuration

            -V is specific verbosity, and can have any of the following arguments
                "in" is verbose incoming osc message
                "out" is verbose outgoing osc message
                "listen" is verbose listen port number
                "command" is verbose command and control port number
                "forward" is verbose forwarding list
                These can be used in combination
                    i.e. -V in out is both verbose incoming and outgoing osc messages

            -v and -V are mutually

            -q is globally quite, it will ignore all configuration verbosity options and run
                OSC Whispers in quite mode

            -Q specific quite may be a good option to disable verbosity options that are set up 
                in the configuration file, however it will remain mutually exclusive from specific 
                verbosity

    '''
    parser = ArgumentParser(description = 'An Open Sound Control forwarding agent.')

    # Add arguments
    
    # OTW File(s)
    # optionally specify multiple otw files and have all the forwarding definitions loaded
    parser.add_argument('-f', '--file', dest = 'otw', nargs = '+', help = 'Specifies OTW files to be loaded into OSC Whispers.')

    # Verbosity Arguments
    verbosityGroup = parser.add_mutually_exclusive_group()


    # Global verbosity
    verbosityGroup.add_argument('-v', '--verbose', dest = 'verbose', action = 'store_true', help = 'Verbosely output all information')

    # Specific verbosity
    verbosityGroup.add_argument('-V', dest = 'specificVerbosity', choices = ['in', 'out', 'listen', 'command', 'forward'], nargs = '+', help = 'Verbosely output specific information.')

    # Quite Mode
    verbosityGroup.add_argument('-q', '--quite', dest = 'quite', action = 'store_true', help = 'Run without any verbose output regardless of verbosity setting in configuration file.')

    # Set argument values
    args = parser.parse_args()

    # Specific verbosity flags
    if args.specificVerbosity:
        for verboseFlag in args.specificVerbosity:
            if verboseFlag == 'in':
                verboseIncomingOsc = True
            elif verboseFlag == 'out':
                verboseOutgoingOsc = True
            elif verboseFlag == 'listen':
                verboseListenPort = True
            elif verboseFlag == 'command':
                verboseCommandPort = True
            elif verboseFlag == 'forward':
                verboseForwardingList = True

    # Global verbosity flags
    if args.verbose:
        verboseIncomingOsc = True
        verboseOutgoingOsc = True
        verboseListenPort = True
        verboseCommandPort = True
        verboseForwardingList = True

    # Quite mode
    if args.quite:
        verboseIncomingOsc = False
        verboseOutgoingOsc = False
        verboseListenPort = False
        verboseCommandPort = False
        verboseForwardingList = False

    # Load the forwarding destinations from file
    # OTW file constants
    PATH_PREFIX_FILE_INDEX = 0
    TRUNCATE_INDICATOR_FILE_INDEX = 1
    DESTINATIONS_START_INDEX = 2

    # run for loop through all args.otw entries
    for otwFileName in args.otw:
        # File load vars
        otwFile = open(otwFileName, 'r')
        otwLines = otwFile.read().split('\n')
        otwFile.close()
    
        # Parse OTW lines
        # do this like the new config file comment methods
        for lineRead in otwLines:
            if lineRead: 
                lineReadProtoComment = lineRead.split(OTW_COMMENT_SYMBOL)[OTW_PROTO_COMMENT].split()
                if lineRead.strip().startswith("/"):
                    #parse forwarding destinations line
                    forwardingPathPrefix = lineReadProtoComment[PATH_PREFIX_FILE_INDEX].strip('/')
                    if lineReadProtoComment[TRUNCATE_INDICATOR_FILE_INDEX] == "+":
                        #do not truncate prefix of path
                        truncatePathPrefix = False
                    elif lineReadProtoComment[TRUNCATE_INDICATOR_FILE_INDEX] == "-":
                        #truncate prefix of path
                        truncatePathPrefix = True
                    else:
                        # Throw better exceptions
                        print('Error: OTW file ' + otwFileName  + ' contains incorrect truncation indicator')
                        exit(ERROR)
                    
                    pathPrefixInfo = [forwardingPathPrefix,truncatePathPrefix]
    
                    for destination in range(DESTINATIONS_START_INDEX,len(lineReadProtoComment)):
                        '''
                        load the destinations into its own list, and load the index of the 
                        destination into the forwardingList
                        It will have to scan back through the destination (server list) to make 
                        sure it doesnt store duplicates
                        '''
                        messageIP = lineRead.split()[destination].split(':')[IP_INDEX]
                        messagePort = int(lineRead.split()[destination].split(':')[PORT_INDEX])
                        tempMessageTargets.append([messageIP, messagePort])
    
                        for targetScan in tempMessageTargets:
                            oscMessageTargets.append([targetScan[IP_INDEX], targetScan[PORT_INDEX]])
                            targetId = len(oscMessageTargets) - 1
                        targetIdList.append(targetId)
                        tempMessageTargets=[]
    
                    forwardingList.append([pathPrefixInfo, targetIdList])
                    reusedTarget = False
                    targetIdList = []

### ---------------------------------------------------------------------------------------


### Create functions 
            

#setup OSC Server
try:
    if verboseListenPort == True:
        print('Listening on port: ', end = '')
        print(listenPort)
    oscListenServer = Server(listenPort)
except ServerError as error:
    exit(error)


#setup OSC clients
for target in oscMessageTargets:
    try:
        oscTarget.append(Address(target[IP_INDEX], target[PORT_INDEX]))
    except AddressError as error:
        exit(error)




def sendOSC(target, path, args):
    #send osc messages in this function
    libloSend='send(target, path'
    for eachArg in enumerate(args):
        libloSend+=', args['+str(eachArg[ENUMERATE_ITERATE_INDEX])+']'
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
    for eachList in forwardingList:
        if eachList[PATH_INFO_LIST_INDEX][PATH_PREFIX_INDEX]==pathPrefix(path):
            if eachList[PATH_INFO_LIST_INDEX][TRUNCATE_INDICATOR_INDEX]==True:
                for eachTarget in eachList[CLIENT_TARGET_LIST_INDEX]:
                    sendOSC(oscTarget[eachTarget], truncatePathPrefix(path), args)
            else:
                for eachTarget in eachList[CLIENT_TARGET_LIST_INDEX]:
                    sendOSC(oscTarget[eachTarget], path, args)
    return
        



### This may need to be in function?_
#register OSC Listen method
oscListenServer.add_method(None, None, forwardMessage)

### Startup verbosity whould be a function
#output Startup verbosity
if verboseForwardingList==True:
    print()
    for eachList in forwardingList:
        #make this output look nicer
        print('Path with prefix /', end='')
        print(eachList[PATH_INFO_LIST_INDEX][PATH_PREFIX_INDEX], end=' ')
        if eachList[PATH_INFO_LIST_INDEX][TRUNCATE_INDICATOR_INDEX]==True:
            print('will truncate path prefix.')
        else:
            print('will not truncate path prefix.')
        print('Then it will forward to:')
        for target in eachList[CLIENT_TARGET_LIST_INDEX]:
            print('IP: ', end='')
            print(oscMessageTargets[target][IP_INDEX], end='    Port: ')
            print(str(oscMessageTargets[target][PORT_INDEX]))
        print()



##  This should be in 2nd __main__
#main loop
if __name__ == "__main__":
    while True:
        oscListenServer.recv(MAIN_LOOP_LATENCY)
