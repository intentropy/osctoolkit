#!/usr/bin/env python
'''
    osctoolkit module
        This module contains all methods and classes required by scripts that run under osctookit
'''

# Import modules
from argparse import ArgumentParser
from liblo import Address, AddressError, Server, ServerError, send
from sys import exit
from os.path import isfile


# Global enumeration indicies constants
ENUMERATE_ITERATE_INDEX = 0
ENUMERATE_VALUE_INDEX = 1



### --- OSC Listen Class ---------------------------------------------------------------------
class OSCListen:
    """This class contains all methods and properties for running OSC Listen"""
    
    # Declare class variables
    exitCall = False
    oscListenServers = []

    class ConfigFile:
        """Load and parse OSC Toolkit configuration file."""
        ## Class variables for loading and parsing the configuration file
        # Declare config constants
        CONFIG_PROPERTY_ARG = 0
        CONFIG_VALUE_ARG = 1
        CONFIG_PROTO_COMMENT = 0
        CONFIG_COMMENT_SYMBOL = '#'
        
    
        def __init__(self, configFileLocations):
            # declare global config and argument vars with default values
            self.verboseListenPorts = False
            self.verboseMotd = False
            self.listenPorts = []
            self.motd = ''
    
            # Run initialization functions
            self.configData = self.parseConfigFile(self.loadConfigFile(configFileLocations))
        
        def loadConfigFile(self, configFileLocations):
            ## Load Config File
            for checkConf in configFileLocations:
                if isfile(checkConf):
                    configFileLocation = checkConf
                    break
            configFile = open(configFileLocation, 'r')
            configFileLines = configFile.read().split('\n')
            configFile.close()
            return configFileLines
    
        def parseConfigFile(self, configLines):
        # Parse config file lines
            for lineRead in configLines:
                if lineRead:
                    lineReadProtoComment = lineRead.split(self.CONFIG_COMMENT_SYMBOL)[self.CONFIG_PROTO_COMMENT].split(' ')
                    # Verbosity Settings
                    if lineReadProtoComment[self.CONFIG_PROPERTY_ARG] == 'osclisten.verbose_listen_ports':
                        self.verboseListenPorts = bool(int(lineReadProtoComment[self.CONFIG_VALUE_ARG]))
                    
                    if lineReadProtoComment[self.CONFIG_PROPERTY_ARG] == 'osclisten.verbose_motd':
                        self.verboseMotd = bool(int(lineReadProtoComment[self.CONFIG_VALUE_ARG]))

                    if lineReadProtoComment[self.CONFIG_PROPERTY_ARG] == 'osclisten.motd':
                        for configArg in range(self.CONFIG_VALUE_ARG, len(lineReadProtoComment)):
                            self.motd += lineReadProtoComment[configArg] + ' '
            
                    # OSC Settings
                    if lineReadProtoComment[self.CONFIG_PROPERTY_ARG] == 'osclisten.listen_port':
                        self.listenPorts.append(int(lineReadProtoComment[self.CONFIG_VALUE_ARG]))

            return {'verboseListenPorts': self.verboseListenPorts, 
                    'listenPorts': self.listenPorts, 
                    'verboseMotd': self.verboseMotd, 
                    'motd': self.motd}
        
    
    class ParseArgs:
        """Parse command line arguments"""
    
        def __init__(self):
            # declare global config and argument vars with default values
            self.verboseListenPorts = False
            self.verboseMotd = False
            self.listenPorts = []
    
            # run initilization methods
            self.argData = self.parse()
    
        def parse(self):
            ## Parse Arguments
            # These values may potentially overwrite config arguments
            parser = ArgumentParser(description = 'Display incoming Open Sound Control messages.')
            
            ## Add arguments
            # List additional listen ports
            parser.add_argument("-l",
                    "--listen", 
                    dest = "ports", 
                    nargs = "+", 
                    type = int, 
                    help = "List additional ports to listen for OSC messages on.")

            # Verbosely display listen ports
            parser.add_argument("-v", 
                    "--verbose", 
                    action = "store_true", 
                    help = "Verbosely display listen ports and MOTD on startup.")

            # Add specific verbosity for listen ports and MOTD (see as OSC Whispers arg parsing)
            # Add quiet mode to halt verbosity
            # Add specific quiet mode (see OSC Whispers arg parsing)

            # Set argument vars
            args = parser.parse_args()
            if args.verbose:
                self.verboseListenPorts = self.verboseMotd = args.verbose
            if args.ports:
                for port in args.ports:
                    self.listenPorts.append(port)
            return {'verboseListenPorts': self.verboseListenPorts, 
                    'verboseMotd': self.verboseMotd, 
                    'listenPorts': self.listenPorts}
        
    
    # Verbosely display listen ports
    def displayListenPorts(listenPorts):
        for portIdNum in listenPorts:
            print('Listening for OSC on port number: ', end = '')
            print(portIdNum)
        print()
        return
            
    
    # Setup listen ports
    def setupOSCServers(listenPorts):
        try:
            for oscServerId in listenPorts:
                OSCListen.oscListenServers.append(Server(oscServerId))
        except ServerError as  error:
            exit(error)
        return
    
    
    # Build the functions for echoing messages on each port, then regiter as OSC servers
    def buildOSCServers(listenPorts):
        # Setup Constants for building OSC servers
        global EXIT_ARG_INDEX
        EXIT_ARG_INDEX = 0
        COMMAND_OSC_PATH = '/osclisten'
        EXIT_COMMAND_PATH = COMMAND_OSC_PATH + '/exit'
    
        # Setup variables for building the OSC servers
        oscSppDef = []
        oscSppRegistration = []
    
        # Build server per port (spp) fucntion strings
        for eachPort in listenPorts:
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
            oscSppDefLine += '        OSCListen.exitCall = True\n'
            oscSppDefLine += '    else:\n'
            # or else echo the incoming message
            oscSppDefLine += '        print("'+str(eachPort)+': ", end = "")\n'
            oscSppDefLine += '        print(path, end = " ")\n'
            oscSppDefLine += '        print(args)\n'
            oscSppDefLine += '    return'
            oscSppDef.append(oscSppDefLine)
        
        # Build server per port (spp) functions
        for execSppDefLine in oscSppDef:
            exec(execSppDefLine)
        
        # Build server per port (spp) OSC method registration string
        for eachPort in listenPorts:
            oscSppBuild = 'OSCListen.oscListenServers[eachMethod[ENUMERATE_ITERATE_INDEX]].add_method(None, None, oscServer_' + str(eachPort) + ')'
            oscSppRegistration.append(oscSppBuild)
    
        # Register methods for listening on each port as an OSC Server
        for eachMethod in enumerate(oscSppRegistration):
            exec(eachMethod[ENUMERATE_VALUE_INDEX])
        return
    
    def displayMOTD(motd):
        # MOTD variables
        # Set this in config, and maybe on the fly with an argument
        print(motd)
        print()
        return
# ------------------------------------------------------------------------------------------------



# --- OSC Shout Class ----------------------------------------------------------------------------
class OSCShout():
    """This class contains all methods and properties for running OSC Shout"""

    class ParseArgs:
        """Parse command line arguments"""
    
        
        def __init__(self):
            
            # Argument parsing variables
            self.oscPathElements = []
            self.oscTargetPath = ''
            self.targetIp = ''
            self.targetPort = ''
            self.oscArgList = []
    
            # Run intitialization methods
            self.argData = self.parse()
    
        def parse(self):
            # Argument parsing constant
            TARGET_ARG_INDEX = 0
            IP_PORT_PATH_ARG_INDEX = 1
            IP_PORT_PATH_INDEX = 0
            IP_INDEX = 0
            PORT_PATH_INDEX = 1
            PORT_INDEX = 0
            TOP_LEVEL_PATH_INDEX = 1
        
            ## Parse Arguments
            parser = ArgumentParser()
    
            ## Add Arguments
            '''
                The first argument will be an IPv4 address, target port number, and the OSC message 
                path name
                    i.e.    127.0.0.1:9999/foo/bar
        
                All following arguments will be converted into a string, integer, or floating point value,
                then sent in the OSC message.
            '''
            # OSC Target (IP:PORT/PATH)
            parser.add_argument("target", 
                    nargs = 1, 
                    help = "IP:PORT/Path/to/message")
            
            # OSC messages
            parser.add_argument("message", 
                    nargs = "+", 
                    help = "Strings, integers, and floating point values to be sent in the OSC message.")
        
            args = parser.parse_args()
    
            ## Gather ip, port, and path from args.target
            oscIpPortPath = args.target[TARGET_ARG_INDEX]
        
            # Store target IP address
            self.oscTargetIp = oscIpPortPath.split(':')[IP_INDEX]
    
            # Store target port number
            self.oscTargetPort = int(oscIpPortPath.split(':')[PORT_PATH_INDEX].split('/')[PORT_INDEX])
    
            # Store OSC message path
            oscPathElements = []
            for pathElement in enumerate(oscIpPortPath.split(':')[PORT_PATH_INDEX].split('/')):
                if pathElement[ENUMERATE_ITERATE_INDEX] >= TOP_LEVEL_PATH_INDEX:
                    oscPathElements.append(pathElement[ENUMERATE_VALUE_INDEX])
            for pathElement in oscPathElements:    
                self.oscTargetPath += '/' + pathElement
                    
            # Gather oscArgList from args.message and convert to an integer, floating point, or string
            for oscArg in args.message:
                # If the message is surrounded by " or ' then do not convert from a string
                try:
                    # Conver to an integer
                    self.oscArgList.append(int(oscArg))
                except:
                    try:
                        # Convert to a floating point value
                        self.oscArgList.append(float(oscArg))
                    except:
                        # Keep as a string
                        self.oscArgList.append(str(oscArg))
            return {'oscTargetIp': self.oscTargetIp,
                    'oscTargetPort': self.oscTargetPort,
                    'oscTargetPath': self.oscTargetPath,
                    'oscArgList': self.oscArgList}

    
    def sendOSC(target, path, messages):
        ## Sends OSC Message
        # Create a string for a liblo.send() command
        libloSend = 'send(target, path'
        '''
            OSC message arguments are sent into the function as a list called messages.  The list 
            entries of messages must be added to the end of a string executed as a liblo.send() 
            command.  Each entry in the messages list must be added near the end of the command
            string, one by one, as the messages list itself, enumerating through each of the 
            indicies in messages.
        '''
        for eachMessage in enumerate(messages):
            libloSend += ', messages[' + str(eachMessage[ENUMERATE_ITERATE_INDEX]) + ']'
        libloSend += ')'
        exec(libloSend)
        return
    
    
    def createOSCClient(oscTargetIp, oscTargetPort):
        # Create OSC Client
        try:
            return Address(oscTargetIp, oscTargetPort)
        except AddressError as error:
            exit(error)

# ------------------------------------------------------------------------------------------------



# --- OSC Whispers Class ----------------------------------------------------------------------------
class OSCWhispers():
    """This class contains all methods and properties for running OSC Whispers"""

# ------------------------------------------------------------------------------------------------



# --- OSC Presets Class ----------------------------------------------------------------------------
class OSCPresets():
    """This class contains all methods and properties for running OSC Presets"""

# ------------------------------------------------------------------------------------------------
