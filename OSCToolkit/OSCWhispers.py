#!/usr/bin/env python3
'''
OSC Whispers
    oscwhispers.py
      Written by: Shane Huter

    Required Dependencies:  python >= 3.5, pyliblo

      This python script, and all of osctoolkit is licensed
      under the GNU GPL version 3.

      The OSC Whispers module contains all of the functions and classes required
      to run OSC Whispers

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
    * Verbosity is currently broken and needs to rebuilt in its function
    * Add a command and control OSC Server for issuing commands to oscwhipsers using OSC messages
    * Add an OSC Client to send debug/logging information out as a OSC Message
        Message could be things like a "ready to go" message, "shutting down" message,
        and maybe errors, etc...
    * Add logging
'''


#PROGRAM CONST
ENUMERATE_ITERATE_INDEX = 0
ENUMERATE_VALUE_INDEX = 1



## Load config file and parse arguments
class ConfigFile:
    """ Load and parse OSC Toolkit configuration file for OSC Whispers. """

    ## Class variables for configuration file parsing
    # Declare configuration file contants
    '''
    make the constant CONFIG_PROPERTY_ARG
    become CONFIG_PROPERY_INDEX
    ALL list index constants must end in _INDEX
    ARG in not needed

    fix in all modules
    '''
    
    CONFIG_PROPERTY_ARG = 0
    CONFIG_VALUE_ARG = 1
    CONFIG_PROTO_COMMENT = 0 
    CONFIG_COMMENT_SYMBOL = '#' 

    def __init__(self, configFileLocations):
        """ Initialization procedure for ConfigFile. """

        # Declare config arguments with default values defaults
        self.verboseListenPort = False
        self.verboseIncomingOsc = False
        self.verboseOutgoingOsc = False
        self.verboseForwardingRules = False
        self.verboseCommandPort = False
        self.serverListenPort = 9000

        # Run initialization fucntions
        self.configData = self.parseConfigFile(
                self.loadConfigFile(
                    configFileLocations
                    ))

    def loadConfigFile(self, configFileLocations):
        """ Load the configuration file. """

        ## Load config file
        #  Rebuild and use 'with ... as ... '
        for checkConf in configFileLocations:
            if isfile(checkConf):
                configFileLocation = checkConf
                break
        configFile = open(configFileLocation, 'r')
        configLines = configFile.read().split('\n')
        configFile.close()
        return configLines

    def parseConfigFile(self, configLines):
        # Parse config file lines
        for lineRead in configLines:
            if lineRead:
                # Seperate the data in each line by whitespace
                lineData = lineRead.split(self.CONFIG_COMMENT_SYMBOL)[self.CONFIG_PROTO_COMMENT].split(' ')
                # Verbosity settings
                if lineData[self.CONFIG_PROPERTY_ARG] == 'oscwhispers.verbose_listen_port':
                    self.verboseListenPort = bool(
                            int(
                                lineData[self.CONFIG_VALUE_ARG]
                                )
                            )
    
                # add verbose command port for displaying oscwhipsers command and control port number
                
                if lineData[self.CONFIG_PROPERTY_ARG] == 'oscwhispers.verbose_incoming_osc':
                    self.verboseIncomingOsc = bool(
                            int(
                                lineData[self.CONFIG_VALUE_ARG]
                                )
                            )
                
                if lineData[self.CONFIG_PROPERTY_ARG] == 'oscwhispers.verbose_outgoing_osc':
                    self.verboseOutgoingOsc = bool(
                            int(
                                lineData[self.CONFIG_VALUE_ARG]
                                )
                            )
                
                if lineData[self.CONFIG_PROPERTY_ARG] == 'oscwhispers.verbose_forwarding_rules':
                    self.verboseForwardingRules = bool(
                            int(
                                lineData[self.CONFIG_VALUE_ARG]
                                )
                            )
    
        
                # OSC Settings
                if lineData[self.CONFIG_PROPERTY_ARG] == 'oscwhispers.server_listen_port':
                    self.serverListenPort = int(
                            lineData[self.CONFIG_VALUE_ARG]
                            )
        
        return {
                'verboseListenPort': self.verboseListenPort,
                'verboseIncomingOsc': self.verboseIncomingOsc,
                'verboseOutgoingOsc': self.verboseOutgoingOsc,
                'verboseForwardingRules': self.verboseForwardingRules,
                'verboseCommandPort': self.verboseCommandPort,
                'serverListenPort': self.serverListenPort,
                }



class ParseArgs:
    """Parse command line arguments for OSC Whispers"""
    '''
        Argument Notes:
            OTW Files:
            To specify otw files pass
                -f or --files [FILES]
                    specify files on command line

                -d or --daemonize
                    specified files are loaded from configuration file.  This allows script to be
                    enabled as a service.  Daemonize is mutually exclusive from files.
            
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
    
    def __init__(self, configData):
        # Declare argument variables with default values
        self.verboseIncomingOsc = configData['verboseIncomingOsc']
        self.verboseOutgoingOsc = configData['verboseOutgoingOsc']
        self.verboseListenPort = configData['verboseListenPort']
        self.verboseCommandPort = configData['verboseCommandPort']
        self.verboseForwardingRules = configData['verboseForwardingRules']
        self.otwFileLocations = []
        
        # Run initilization functions
        self.argData = self.parse()


    def parse(self):
        parser = ArgumentParser(description = 'An Open Sound Control forwarding agent.')
        
         ## Add arguments
        
        # OTW File(s)
        # optionally specify multiple otw files and have all the forwarding definitions loaded
        parser.add_argument(
                '-f', 
                '--file', 
                dest = 'otw', 
                nargs = '+', 
                help = 'Specifies OTW files to be loaded into OSC Whispers.',
                )
    
        # Verbosity Arguments
        verbosityGroup = parser.add_mutually_exclusive_group()
    
    
        # Global verbosity
        verbosityGroup.add_argument(
                '-v', 
                '--verbose', 
                dest = 'verbose', 
                action = 'store_true', 
                help = 'Verbosely output all information',
                )
        
        # Specific verbosity
        verbosityGroup.add_argument(
                '-V', 
                dest = 'specificVerbosity', 
                choices = ['in', 'out', 'listen', 'command', 'forward'], 
                nargs = '+', 
                help = 'Verbosely output specific information.',
                )
        
        # Quite Mode
        verbosityGroup.add_argument(
                '-q', 
                '--quite', 
                dest = 'quite', 
                action = 'store_true', 
                help = 'Run without any verbose output regardless of verbosity setting in configuration file.',
                )
        
        # Set argument values
        args = parser.parse_args()

        # Load and parse otw files passed as arguments
        if args.otw:
            # Load OTW Files into a list for the argData dictionary
            for arg in args.otw:
                self.otwFileLocations.append(arg)
        else:
            # If there are no OTW files to load rules from then print help and exit
            # If -d is passed then there will be no args.otw
            exit(parser.print_help())
    
        # Specific verbosity flags
        if args.specificVerbosity:
            for verboseFlag in args.specificVerbosity:
                if verboseFlag == 'in':
                    self.verboseIncomingOsc = True
                if verboseFlag == 'out':
                    self.verboseOutgoingOsc = True
                if verboseFlag == 'listen':
                    self.verboseListenPort = True
                if verboseFlag == 'command':
                    self.verboseCommandPort = True
                if verboseFlag == 'forward':
                    self.verboseForwardingRules = True
        
        # Global verbosity flags
        if args.verbose:
            self.verboseIncomingOsc = True
            self.verboseOutgoingOsc = True
            self.verboseListenPort = True
            self.verboseCommandPort = True
            self.verboseForwardingRules = True
        
        # Quite mode
        if args.quite:
            self.verboseIncomingOsc = False
            self.verboseOutgoingOsc = False
            self.verboseListenPort = False
            self.verboseCommandPort = False
            self.verboseForwardingRules = False
        
        return {
                'verboseListenPort':        self.verboseListenPort,
                'verboseIncomingOsc':       self.verboseIncomingOsc,
                'verboseOutgoingOsc':       self.verboseOutgoingOsc,
                'verboseForwardingRules':   self.verboseForwardingRules,
                'otwFileLocations':         self.otwFileLocations,
                }



class OTWFiles:
    """
    This class takes a list of OTW File locations and parses the data into an
    OSC Client list and a forwarding ruleset.
    """
    
    # Declare OTWFiles() class variables
    OTW_PROTO_COMMENT = 0
    OTW_COMMENT_SYMBOL = '#'
    OTW_PATH_SYMBOL = '/'
    OTW_PORT_SYMBOL = ':'
    OTW_NO_PATH_ALIAS_LENGTH = 1
    
    PATH_PREFIX_INDEX = 0
    TRUNCATE_INDICATOR_INDEX = 1
    TARGETS_START_INDEX = 2

    OSC_TARGETS_ID_INDEX = 0
    OSC_TARGETS_TARGET_INDEX = 1

    # These indexes refer to data inside of oscTargets
    OSC_TARGET_IP_INDEX = 0
    OSC_TARGET_PORT_INDEX = 1
    OSC_TARGET_ALIAS_INDEX = 2
    
    # Used for splitting path aliases from ports
    OSC_TARGET_PORT_SPLIT_PORT_INDEX = 0
    OSC_TARGET_PORT_SPLIT_ALIAS_START_INDEX = 1

    
    
    def __init__(self, otwFiles):
        # Declare variables for instatiated object
        oscClients = []

        # Run initialization functions
        self.otwFileData = self.parseOtwFiles(self.loadOtwFiles(otwFiles))


    def loadOtwFiles(self, otwFiles):
        """ Load the forwarding destinations from file. """
        # OTW file constants
        # rebuild using 'with ... as ...'
    
        # run for loop through all args.otw entries
        otwLines = []
        for otwFileName in otwFiles:
            # File load vars
            otwFile = open(otwFileName, 'r')
            otwLines += otwFile.read().split('\n')
            otwFile.close()
        return otwLines

    
    
    def buildOSCPath(self, pathElements = [] ):
        """ Take a list of path elements (directory names) and return a string representing an OSC path """
        oscPath = ''
        for element in pathElements:
            oscPath += '/' + element
        return oscPath
    


    def oscTargetData(self, target = '' ):
        """ Take an osc target 'IP:PORT(/ALIAS) and return a  list of osc target data for each target. """
        # Used to parse target information
        OTW_PATH_SYMBOL = '/'
        OTW_PORT_SYMBOL = ':'
        OTW_NO_PATH_ALIAS_LENGTH = 1

        # Used for splitting path aliases from ports
        OSC_TARGET_PORT_SPLIT_PORT_INDEX = 0
        OSC_TARGET_PORT_SPLIT_ALIAS_START_INDEX = 1

        # These indexes refer to data inside of oscTargets
        OSC_TARGET_IP_INDEX = 0
        OSC_TARGET_PORT_INDEX = 1
        OSC_TARGET_ALIAS_INDEX = 2

        # Get ip
        ip = target.split(OTW_PORT_SYMBOL)[OSC_TARGET_IP_INDEX]
        
        # Determine if there is a path alias

        if len(
                target.split(
                    OTW_PATH_SYMBOL
                    )
                ) == OTW_NO_PATH_ALIAS_LENGTH:
                
            # There is no path alias
            port = target.split(OTW_PORT_SYMBOL)[OSC_TARGET_PORT_INDEX]
            alias = None

        else:
            # There is a path alias
            port = target.split(
                    OTW_PORT_SYMBOL
                    )[OSC_TARGET_PORT_INDEX].split(
                            OTW_PATH_SYMBOL
                            )[OSC_TARGET_PORT_SPLIT_PORT_INDEX]

            alias = self.buildOSCPath(
                    target.split(
                        OTW_PORT_SYMBOL
                        )[OSC_TARGET_PORT_INDEX].split(
                            OTW_PATH_SYMBOL
                            )[OSC_TARGET_PORT_SPLIT_ALIAS_START_INDEX:]
                        )

        return [
            ip ,
            port ,
            alias ,
            ]

    
    
    def parseOtwFiles(self, otwLines):
        """ Parse lines from OTW file into a forwarding ruleset. """
        '''
        OTW File Parsing

            Consider putting each for lineRead section in a seperate function
                
            1st all of the targets should be put in a list oscTargets
                * Change DESTINATIONS to TARGET in class const
                * Only unique targets are stored in the list
                * Targets are givin an ID (int)
                * Targets are [ID, [IP, PORT] ]

            2nd create the forwarding rules list
                * Forwarding rules are [ [Path Prefix, Truncation Bool], [Target ID, Target ID, ...] ]

            Finally a dictionary is returned for the OSC functions to use
                * dictionary name is otwFileData
                * Its contents are forwardingRules, and oscTargets

            In the OSC functions OSC clients (oscClients) will be created with the
            OSC targets (oscTargets), and matched rules can be forwarded to respective
            clients.
        '''

        ## Build oscTargets list
        oscTargets  = []
        allOscTargets = [] 
        preIdOscTargets = []
        
        for lineRead in otwLines:
            if lineRead: 
                # Seperate the data in each line by whitespace and ignore data post comment symbol
                lineData = lineRead.split(self.OTW_COMMENT_SYMBOL)[self.OTW_PROTO_COMMENT].split()
                if lineData:

                    # Iterate through the OSC tagets for the forwarding rule
                    for dataIndex in range(
                            self.TARGETS_START_INDEX , 
                            len(lineData)
                            ):

                        # Debug print oscTargetData
                        allOscTargets.append(
                                self.oscTargetData(
                                    lineData[dataIndex]
                                    )
                                )
                            
                        # Store only unique targets in preIdOscTargets
                        for target in allOscTargets:
                            redundantTarget = False
                            for storedTarget in preIdOscTargets:
                                if target == storedTarget:
                                    redundantTarget = True
                                    break
                            if redundantTarget == False:
                                preIdOscTargets.append(target)

        # Enumerate preIdOscTargets and append the value and iteration number to oscTargets
        for target in enumerate(preIdOscTargets):
            oscTargets.append([
                    target[ENUMERATE_ITERATE_INDEX], 
                    target[ENUMERATE_VALUE_INDEX],
                    ])
        
        
        ## Build forwarding rules list
        forwardingRules = []
        pathPrefixRules = []
        
        for lineRead in otwLines:
            if lineRead: 
                # Seperate the data in each line by whitespace
                lineData = lineRead.split(self.OTW_COMMENT_SYMBOL)[self.OTW_PROTO_COMMENT].split()
                if lineData:

                    #parse forwarding destinations line
                    forwardingPathPrefix = lineData[self.PATH_PREFIX_INDEX].strip('/')

                    # Determine the truncation indicator boolean
                    if lineData[self.TRUNCATE_INDICATOR_INDEX] == "+":
                        #do not truncate prefix of path
                        truncatePathPrefix = False
                    elif lineData[self.TRUNCATE_INDICATOR_INDEX] == "-":
                        #truncate prefix of path
                        truncatePathPrefix = True
                    else:
                        # Throw better exceptions
                        # raise
                        print('Error: OTW file ' + otwFileName  + ' contains incorrect truncation indicator')
                        exit(ERROR)

                    
                    
                    # Check all targets in OTW File agains oscTargets and store ID list
                    idList = []

                    '''
                        When checking for the ID of the target Path alias must also be checked
                    '''
                    
                    for dataIndex in range(
                            self.TARGETS_START_INDEX , 
                            len(lineData)
                            ):


                        for target in oscTargets:
                            if self.oscTargetData(
                                    lineData[dataIndex]
                                    ) == target[self.OSC_TARGETS_TARGET_INDEX]:
                                idList.append(
                                        target[self.OSC_TARGETS_ID_INDEX] 
                                        )


                    # Finally, build the forwarding rule list
                    forwardingRules.append(
                            [
                                forwardingPathPrefix, 
                                truncatePathPrefix, 
                                idList
                                ]
                            )

        return {
                'forwardingRules': forwardingRules,
                'oscTargets': oscTargets,
                }



### Create functions 
class OSC:
    """This class contains all functions for Open Sound Control operations"""
    
    # Declare OSC class constants and variables
    MAIN_LOOP_LATENCY = 1

    IP_INDEX = 0
    PORT_INDEX = 1
    ALIAS_INDEX = 2

    CLIENT_ID_INDEX = 0
    TARGET_INDEX = 1

    PATH_PREFIX_INDEX = 0
    TRUNCATION_INDICATOR_INDEX = 1
    CLIENT_TARGET_LIST_INDEX = 2

    PATH_PREFIX_SPLIT_INDEX = 1

    
    
    def __init__(self, serverListenPort, forwardingRules, oscTargets):
        # Declare instatiation variables
        self.forwardingRules = forwardingRules

        # OSC target information (enumerate for client IDs)
        self.oscTargets = []
        for target in oscTargets:
            self.oscTargets.append(
                    target[
                        self.TARGET_INDEX
                        ]
                    )

        ## Run initializtion functions
        # Setup the OSC server for incoming messages
        self.listenServer = self.setupOscServer(serverListenPort)

        # Setup the OSC clients
        self.oscClients = self.setupOscClients(oscTargets)


    
    def sendOSC(self, target, path, args):
        #send osc messages in this function
        libloSend='send(target, path'
        for eachArg in enumerate(args):
            libloSend+=', args['+str(eachArg[ENUMERATE_ITERATE_INDEX])+']'
        libloSend+=')'
        exec(libloSend)
        return



    def forwardMessage(self, path, args):
        """ Forward the osc Message based on forwarding rules. """
        # This is a special function called as a liblo method (add_method) 

        # Check message against the forwarding rules
        for rule in self.forwardingRules:
            
            # Check the path prefix against the forwarding rules
            if rule[self.PATH_PREFIX_INDEX] == self.pathPrefix(path):

                
                # Check if the matching rule has a truncation indicator
                if rule[self.TRUNCATION_INDICATOR_INDEX]:
                    # Truncaton indicator

                    for client in rule[self.CLIENT_TARGET_LIST_INDEX]:

                        clientAlias = self.oscTargets[client][self.ALIAS_INDEX]
                        if clientAlias:
                            # Alias the path
                            self.sendOSC(
                                    self.oscClients[client], 
                                    clientAlias, 
                                    args,
                                    )
                        else:
                            self.sendOSC(
                                    self.oscClients[client], 
                                    self.truncatePathPrefix(path), 
                                    args,
                                    )

                else:

                    for client in rule[self.CLIENT_TARGET_LIST_INDEX]:
                        clientAlias = self.oscTargets[client][self.ALIAS_INDEX]
                        if clientAlias:
                            # Alias the path
                            self.sendOSC(
                                    self.oscClients[client], 
                                    clientAlias, 
                                    args,
                                    )
                        else:
                            self.sendOSC(
                                    self.oscClients[client], 
                                    path, 
                                    args,
                                    )
        return



    def setupOscServer(self, serverListenPort):
        #setup OSC Server
        try:
    
            oscListenServer = Server(serverListenPort)
            
            #register OSC Listen method
            oscListenServer.add_method(
                    None, 
                    None, 
                    self.forwardMessage,
                    )

        except ServerError as error:
            exit(error)
        return oscListenServer



    def setupOscClients(self, oscMessageTargets):
        #Create OSC clients from a list of targets
        oscClients = []
        for target in oscMessageTargets:
            try:
                oscClients.append(
                        Address(
                            target[OTWFiles.OSC_TARGETS_TARGET_INDEX][self.IP_INDEX] , 
                            target[OTWFiles.OSC_TARGETS_TARGET_INDEX][self.PORT_INDEX] ,
                            )
                        )
            except AddressError as error:
                exit(error)
        return oscClients



    def truncatePathPrefix(self, inPath):
        # Remove a paths top level
        STARTING_NON_PATH_PREFIX_INDEX = 2
        outPath = ''
        for dirs in range(STARTING_NON_PATH_PREFIX_INDEX, len(inPath.split('/'))):
            outPath += '/' + inPath.split('/')[dirs]
        return outPath



    def pathPrefix(self, inpath):
        # Return the a paths top level
        prefix = inpath.split('/')[self.PATH_PREFIX_SPLIT_INDEX]
        return prefix



def verboseOutput():
    # Needs to be repaired

    '''
    if verboseListenPort:
        print('Listening on port: ', end = '')
        print(serverListenPort)
    '''

    # Output Startup verbosity
    if verboseForwardingRules:
        print()
        for eachRule in forwardingRule:
            #make this output look nicer
            print('Path with prefix /', end='')
            print(eachList[OSC.PATH_INFO_LIST_INDEX][OSC.PATH_PREFIX_INDEX], end=' ')
            if eachList[OSC.PATH_INFO_LIST_INDEX][self.TRUNCATE_INDICATOR_INDEX]==True:
                print('will truncate path prefix.')
            else:
                print('will not truncate path prefix.')
            print('Then it will forward to:')
            for target in eachList[OSC.CLIENT_TARGET_LIST_INDEX]:
                print('IP: ', end='')
                print(oscMessageTargets[target][OSC.IP_INDEX], end='    Port: ')
                print(str(oscMessageTargets[target][OSC.PORT_INDEX]))
            print()


