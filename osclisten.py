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

## Import modules
from argparse import ArgumentParser
from liblo import Server, ServerError
from sys import exit
from os.path import isfile

## PROGRAM CONST
CLEAN = 0
ENUMERATE_ITERATE_INDEX = 0
ENUMERATE_VALUE_INDEX = 1


if __name__ == '__main__':
    # Declare config constants
    CONFIG_PROPERTY_ARG = 0
    CONFIG_VALUE_ARG = 1
    CONFIG_PROTO_COMMENT = 0
    CONFIG_FILE_LOCATIONS = ['osctoolkit.conf', '/home/$USER/.config/osctoolkit.conf', '/etc/osctoolkit.conf']
    CONFIG_COMMENT_SYMBOL = '#'
    
    # declare global config and argument vars with default values
    global verboseListenPorts
    verboseListenPorts = False
    global listenPort
    listenPort = []
    
    for checkConf in CONFIG_FILE_LOCATIONS:
        if isfile(checkConf):
            configFileLocation = checkConf
            break
    ## Load Config File
    configFile = open(configFileLocation, 'r')
    configLines = configFile.read().split('\n')
    configFile.close()
    for lineRead in configLines:
        if lineRead:
            lineReadProtoComment = lineRead.split(CONFIG_COMMENT_SYMBOL)[CONFIG_PROTO_COMMENT].split(' ')
            # Verbosity Settings
            if lineReadProtoComment[CONFIG_PROPERTY_ARG] == 'osclisten.verbose_listen_ports':
                verboseListenPorts = bool(int(lineRead.split()[CONFIG_VALUE_ARG]))
    
            # OSC Settings
            if lineReadProtoComment[CONFIG_PROPERTY_ARG] == 'osclisten.listen_port':
                listenPort.append(int(lineRead.split()[CONFIG_VALUE_ARG]))
    
    ## Parse Arguments
    # These values may potentially overwrite config arguments
    parser = ArgumentParser()
    # Add arguments
    #list additional listen ports
    parser.add_argument("-l", "--listen", nargs = "+", type = int, help = "List additional ports to listen for OSC messages on.")
    parser.add_argument("-v", "--verbose", action = "store_true", help = "Verbosely display listen ports on startup.")
    # Set argument vars
    args = parser.parse_args()
    if args.verbose:
        verboseListenPorts = args.verbose
    if args.listen:
        for port in args.listen:
            listenPort.append(port)
    

# Verbosely display listen ports
def displayListenPorts():
    for portIdNum in listenPort:
        print('Listening for OSC on port number: ', end = '')
        print(portIdNum)
        

# Setup listen ports
def setupOSCServers():
    global oscListenServer
    oscListenServer = []
    try:
        for oscServerId in listenPort:
            oscListenServer.append(Server(oscServerId))
    except ServerError as  error:
        print(str(error))
        exit(error)


# Build the functions for echoing messages on each port, then regiter as OSC servers
def buildOSCServers():
    # Setup Constants for building OSC servers
    global EXIT_ARG_INDEX
    EXIT_ARG_INDEX = 0
    COMMAND_OSC_PATH = '/osclisten'
    EXIT_COMMAND_PATH = COMMAND_OSC_PATH + '/exit'

    # Setup variables for building the OSC servers
    oscSppDef = []
    oscSppRegistration = []

    # Build server per port (spp) fucntion strings
    for eachPort in listenPort:
        oscSppDefLine = 'def oscServer_' + str(eachPort) + '(path, args):\n'
        #if the path is '/oscwhispers/exit, and the value is 1 then exit
        '''
            The COMMAND_OSC_PATH command parsing and execution should not happen here
                i.e.
                    /osclisten/exit (1 | True | !NULL)
                    should happen elsewhere
                    along with any other OSC Listen specific OSC commands

            Fix  this in future commits
        '''
        oscSppDefLine += '    if path == "'  + EXIT_COMMAND_PATH  +  '" and int(args[EXIT_ARG_INDEX]) == 1:\n'
        oscSppDefLine += '        global exitCall\n'
        oscSppDefLine += '        exitCall = True\n'
        oscSppDefLine += '    else:\n'
        # or else echo the incoming message
        oscSppDefLine += '        print("'+str(eachPort)+':", end = "")\n'
        oscSppDefLine += '        print(path, end = " ")\n'
        oscSppDefLine += '        print(args)\n'
        oscSppDefLine +='    return'
        oscSppDef.append(oscSppDefLine)
    
    # Build server per port (spp) functions
    for execSppDefLine in oscSppDef:
        exec(execSppDefLine)
    
    # Nuild server per port (spp) OSC method registration string
    for eachPort in listenPort:
        oscSppBuild = 'oscListenServer[eachMethod[ENUMERATE_ITERATE_INDEX]].add_method(None, None, oscServer_' + str(eachPort) + ')'
        oscSppRegistration.append(oscSppBuild)

    # Register methods for listening on each port as an OSC Server
    for eachMethod in enumerate(oscSppRegistration):
        exec(eachMethod[ENUMERATE_VALUE_INDEX])

def displayMOTD():
    # MOTD variables
    # Set this in config, and maybe on the fly with an argument
    motd = "Ready...\n"
    print(motd)


## Main Loop
def mainLoop():
    # Main Loop Constants
    MAIN_LOOP_LATENCY = 1

    # Main Loop Variables
    global exitCall
    exitCall = False

    while exitCall == False:
        for oscServerId in oscListenServer:
            oscServerId.recv(MAIN_LOOP_LATENCY)

## Main 
if __name__ == '__main__':
    # Verbosely display listen ports if enabled
    if verboseListenPorts == True:
        displayListenPorts()

        # Display MOTD 
        displayMOTD()

    # Setup, Build, and register each OSC server on each listen port
    setupOSCServers()
    buildOSCServers()
    
    # Call the main loop
    mainLoop()
