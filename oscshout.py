#!/usr/bin/env python
'''
OSC Shout
  oscshout.py

    Written By: Shane Hutter
    
    Required Dependencies:  python >= 3.5, pyliblo

      This python script, and all of OSC_Tools is licensed
      under the GNU GPL version 3

      OSC Shout sends OSC Messages, as integers, floating point values, and
      strings, via the command line.

      OSC Shout is a part of osctoolkit

------------------------------------------------------------------------------

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

#program CONST
IP_PORT_PATH_ARG_INDEX=1
IP_PORT_PATH_INDEX=0
IP_INDEX=0
PORT_PATH_INDEX=1
PORT_INDEX=0
FIRST_PATH_DIR_INDEX=1
ERROR=1
CLEAN=0
HELP_CALL_ARG=1
HELP_ONLY_ARGUMENTS=2

#OSC CONST
LAST_OSC_ARG_INDEX=0
TOTAL_NON_OSC_ARG_INDICES=2

#osc Vars
oscPathDir=[]
oscPath=''
oscArgList=[]

def helpAndExit(exitStatus):
    print('Usage:')
    print('  oscshout [IPv4]:[port][/osc/path] [args...]')
    print()
    print('Optional arguments:')
    print('  -h, --help    Display help and exit.')
    print()
    print('Further Documentation:')
    print('  https://github.com/ShaneHutter/osctoolkit/wiki')
    print()
    sys.exit(exitStatus)

#check for help call
if len(sys.argv)== HELP_ONLY_ARGUMENTS:
    if sys.argv[HELP_CALL_ARG]=='-h' or sys.argv[HELP_CALL_ARG]=='--help':
        helpAndExit(CLEAN)
    
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
