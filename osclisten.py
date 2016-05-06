#!/usr/bin/env python
'''
OSC Listen
  osclisten.py
    
    Written by: Shane Hutter

    Required Dependencies:  python >= 3.5, pyliblo

      OSC Listen listens on any ports listed in the 
      osctoolkit.conf configuration file, and prints any incoming
      message (path and values) to the screen.

      OSC Listen is a part of osctoolkit

      osctoolkit is free software; you can redistribute it and/or modify
      it under the terms of the GNU Lesser General Public License as published
      by the Free Software Foundation, either version 3 of the License, or
      (at your option) any later version.

      osctoolkit is distributed in the hope that it will be useful,
      but WITHOUT ANY WARRANTY; without even the implied warranty of
      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
      GNU Lesser General Public License for more details.

      You should have received a copy of the GNU Lesser General Public License
      along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import liblo, sys

#PROGRAM CONST
ERROR=255
CLEAN=0
ENUM_ITERATE_INDEX=0
ENUM_VALUE_INDEX=1

#OSC CONST
EXIT_ARG_INDEX=0

#program vars
exitCall=False

#OSC vars
listenPort=[]
oscListenServer=[]
echoFunc=[]
echoReg=[]

#load config file and declare global vars
#CONFIG CONST
CONFIG_PROPERTY_ARG=0
CONFIG_VALUE_ARG=1
#config
try:
    configFileName='osctoolkit.conf'
    configFile=open(configFileName,'r')
    configLines=configFile.read().split('\n')
except:
    configFileName='/etc/osctoolkit.conf'
    configFile=open(configFileName,'r')
    configLines=configFile.read().split('\n')
finally:
    configFile.close()
for lineRead in configLines:
    if lineRead!="" and lineRead.strip().startswith('#')==False:
        #verbosity settings
        if lineRead.split()[CONFIG_PROPERTY_ARG]=='osclisten.verbose_listen_ports':
            global verboseListenPorts
            verboseListenPorts=bool(int(lineRead.split()[CONFIG_VALUE_ARG]))

        #OSC Settings
        if lineRead.split()[CONFIG_PROPERTY_ARG]=='osclisten.listen_port':
            listenPort.append(int(lineRead.split()[CONFIG_VALUE_ARG]))
            
#Verbosely display listen ports
if verboseListenPorts==True:
    for portIdNum in enumerate(listenPort):
        print('Listening for OSC on port number: ', end='')
        print(portIdNum[ENUM_VALUE_INDEX])
        
#Setup listen ports
try:
    for oscServerId in enumerate(listenPort):
        oscListenServer.append(liblo.Server(oscServerId[ENUM_VALUE_INDEX]))
except liblo.ServerError as  error:
    print(str(error))
    sys.exit(ERROR)

#build echoMessage fucntion strings
for eachPort in enumerate(listenPort):
    tempEchoFunc='def echoMessage'+str(eachPort[ENUM_VALUE_INDEX])+'(path, args):\n'
    #if the path is '/oscwhispers/exit, and the value is 1 then exit
    tempEchoFunc+='    if path=="/osclisten/exit" and int(args[EXIT_ARG_INDEX])==1:\n'
    tempEchoFunc+='        global exitCall\n'
    tempEchoFunc+='        exitCall=True\n'
    tempEchoFunc+='    else:\n'
    #else echo the incoming message
    tempEchoFunc+='        print("'+str(eachPort[ENUM_VALUE_INDEX])+':", end="")\n'
    tempEchoFunc+='        print(path, end=" ")\n'
    tempEchoFunc+='        print(args)\n'
    tempEchoFunc+='    return'
    echoFunc.append(tempEchoFunc)

#create echoMessage functions
for createFunc in enumerate(echoFunc):
    exec(createFunc[ENUM_VALUE_INDEX])

#build OSC method registration string
for eachPort in enumerate(listenPort):
    tempEchoReg='oscListenServer[eachMethod[ENUM_ITERATE_INDEX]].add_method(None, None, echoMessage'+str(eachPort[ENUM_VALUE_INDEX])+')'
    echoReg.append(tempEchoReg)
    
#register methods for listening on each port
for eachMethod in enumerate(echoReg):
    exec(eachMethod[ENUM_VALUE_INDEX])

#loop and dispatch messages every 10ms
print("Ready...")
print()
while exitCall==False:
    for oscServerId in enumerate(oscListenServer):
        oscServerId[ENUM_VALUE_INDEX].recv(1)
sys.exit(0)
