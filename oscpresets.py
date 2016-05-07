#!/usr/bin/env python
'''
OSC Presets
  oscpresets.py
    
    Written by: Shane Hutter

    Required Dependencies:  python >= 3.5, pyliblo

      OSC Presets will send out a list of Open Sound Control messages, after receiving an OSC Message.

      OSC Presets is a part of osctoolkit

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

import sys, liblo

#PROGRAM CONST
CLEAN=0
ERROR=1
ENUM_ITERATE_INDEX=0
ENUM_VALUE_INDEX=1
OTP_FILE_ARG=1
REQUIRED_ARGUMENTS=2
LOOP_DELAY=1
HELP_CALL_ARG=1
HELP_ONLY_ARGUMENTS=2

#CONFIG CONST
CONFIG_PROPERTY_ARG=0
CONFIG_VALUE_ARG=1

#Other Vars

#Help and exit
def helpAndExit(exitStatus):
    print('Usage:')
    print('  oscpresets [FILENAME]')
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

#Check if the required number of arguments where passed
if len(sys.argv)!=REQUIRED_ARGUMENTS:
    helpAndExit(ERROR)

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
    if (lineRead!="") and (lineRead.strip().startswith('#')==False):
        #verbosity settings
        if lineRead.split()[CONFIG_PROPERTY_ARG]=='oscpresets.verbose_listen_port':
            global verboseListenPort
            verboseListenPort=bool(int(lineRead.split()[CONFIG_VALUE_ARG]))
        if lineRead.split()[CONFIG_PROPERTY_ARG]=='oscpresets.verbose_recieved_id':
            global verboseRecievedId
            verboseRecievedId=bool(int(lineRead.split()[CONFIG_VALUE_ARG]))

        #OSC settings
        if lineRead.split()[CONFIG_PROPERTY_ARG]=='oscpresets.listen_port':
            global listenPort
            listenPort=bool(int(lineRead.split()[CONFIG_VALUE_ARG]))
                        

#register OSC input from config
            
#Load OTP file

#register OSC ouputs from OTP file

#register methods for recieved OSC messages

#Main loop
    #listen for osc messages

sys.exit(CLEAN)
