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

###create more specifuc imports
import liblo, sys

###These values need to be declared non globally in respective functions
## PROGRAM CONST
ERROR=1
CLEAN=0
MAIN_LOOP_LATENCY=1
ENUMERATE_ITERATE_INDEX=0
ENUMERATE_VALUE_INDEX=1
HELP_CALL_ARG=1
HELP_ONLY_ARGUMENTS=2

#CONFIG CONST
CONFIG_PROPERTY_ARG=0
CONFIG_VALUE_ARG=1

#OSC CONST
EXIT_ARG_INDEX=0

#program vars
exitCall=False

#OSC vars
listenPort=[]
oscListenServer=[]
echoFunc=[]
echoReg=[]


###use argparse
#help and exit
def helpAndExit(exitStatus):
    print('Usage:')
    print('  Declare listen ports in the configuration file.')
    print()
    print('Optional arguments:')
    print('  -h, --help    Display help and exit.')
    print()
    print('Further Documentation:')
    print('  https://github.com/ShaneHutter/osctoolkit/wiki')
    print()
    sys.exit(exitStatus)

#check for help call
if len(sys.argv)>= HELP_ONLY_ARGUMENTS:
    if sys.argv[HELP_CALL_ARG]=='-h' or sys.argv[HELP_CALL_ARG]=='--help':
        helpAndExit(CLEAN)
    else:
        helpAndExit(ERROR)

###Either load config in early __name__ == '__main__' space or load inside of an object
#load config file and declare global vars
try:
    configFileName='osctoolkit.conf'
    configFile=open(configFileName,'r')
except:
    configFileName='/etc/osctoolkit.conf'
    configFile=open(configFileName,'r')
finally:
    configLines=configFile.read().split('\n')
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

###Create functions for all the functions and call them in approrpriate places in __name__ == '__main__'
#Verbosely display listen ports
if verboseListenPorts==True:
    for portIdNum in listenPort:
        print('Listening for OSC on port number: ', end='')
        print(portIdNum)
        
#Setup listen ports
try:
    for oscServerId in listenPort:
        oscListenServer.append(liblo.Server(oscServerId))
except liblo.ServerError as  error:
    print(str(error))
    sys.exit(ERROR)

#build echoMessage fucntion strings
for eachPort in listenPort:
    tempEchoFunc='def echoMessage'+str(eachPort)+'(path, args):\n'
    #if the path is '/oscwhispers/exit, and the value is 1 then exit
    tempEchoFunc+='    if path=="/osclisten/exit" and int(args[EXIT_ARG_INDEX])==1:\n'
    tempEchoFunc+='        global exitCall\n'
    tempEchoFunc+='        exitCall=True\n'
    tempEchoFunc+='    else:\n'
    #else echo the incoming message
    tempEchoFunc+='        print("'+str(eachPort)+':", end="")\n'
    tempEchoFunc+='        print(path, end=" ")\n'
    tempEchoFunc+='        print(args)\n'
    tempEchoFunc+='    return'
    echoFunc.append(tempEchoFunc)

#create echoMessage functions
for createFunc in echoFunc:
    exec(createFunc)

#build OSC method registration string
for eachPort in listenPort:
    tempEchoReg='oscListenServer[eachMethod[ENUMERATE_ITERATE_INDEX]].add_method(None, None, echoMessage'+str(eachPort)+')'
    echoReg.append(tempEchoReg)
    
#register methods for listening on each port
###Try putting the ENUMERATE_VALUE_INDEX in the for statement
### for eachMethod in enumerate(echoReg)[ENUMERATE_VALUE_INDEX]
for eachMethod in enumerate(echoReg):
    exec(eachMethod[ENUMERATE_VALUE_INDEX])

### Main segment of code should be inside of __name__ == '__main__' 
#loop and dispatch messages every 10ms
print("Ready...")
print()
while exitCall==False:
    for oscServerId in oscListenServer:
        oscServerId.recv(MAIN_LOOP_LATENCY)
sys.exit(CLEAN)
