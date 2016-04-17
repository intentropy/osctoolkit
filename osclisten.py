#!/bin/python
'''
OSC Listen
  osclisten.py
    
    Written by: Shane Hutter

    Required Dependencies:  python >= 3.5, pyliblo

      This python script, and all of OSC_Tools is licensed
      under the GNU GPL version 3

      This program listens on any ports listed in the 
      osctools.conf configuration file, and prints any incoming
      message (path and values) to the screen.
'''

import liblo, sys

#PROGRAM CONST
ERROR=255
CLEAN=0

#OSC vars
listenPort=[]
oscListenServer=[]

#load config file and declare global vars
#CONFIG CONST
CONFIG_PROPERTY_ARG=0
CONFIG_VALUE_ARG=1
#config
configFileName='osctools.conf'
configFile=open(configFileName,'r')
configLines=configFile.read().split('\n')
configFile.close()
for lineRead in configLines:
    if (lineRead!="") and (lineRead.strip()[0:1]!='#'):
        #verbosity settings
        if lineRead.split()[CONFIG_PROPERTY_ARG]=='osclisten.verbose_listen_ports':
            global verboseListenPorts
            verboseListenPorts=bool(int(lineRead.split()[CONFIG_VALUE_ARG]))

        #OSC Settings
        if lineRead.split()[CONFIG_PROPERTY_ARG]=='osclisten.listen_port':
            listenPort.append(int(lineRead.split()[CONFIG_VALUE_ARG]))
            
#Verbosely display listen ports
if verboseListenPorts==True:
    for portIdNum in range(0,len(listenPort)):
        print('Listening for OSC on port number: ', end='')
        print(listenPort[portIdNum])
        
#Setup listen ports
try:
    for oscServerIdNum in range(0,len(listenPort)):
        oscListenServer.append(liblo.Server(listenPort[oscServerIdNum]))
except liblo.ServerError as  error:
    print(str(error))
    sys.exit(ERROR)

#this funtion is executed when OSC command is received
def echoMessage(path, args):
    #TODO: Also print port number of message
    print(path, end=" ")
    print(args)
    return

#register method for receiveing OSC command
for oscServerIdNum in range(0,len(oscListenServer)):
    oscListenServer[oscServerIdNum].add_method(None, None, echoMessage)

#loop and dispatch messages every 10ms
print("Ready...")
print()
while True:
    for oscServerIdNum in range(0,len(oscListenServer)):
        oscListenServer[oscServerIdNum].recv(1)
