#!/usr/bin/python3
"""
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
"""

## Import modules
from .          import *
from argparse   import ArgumentParser
from getpass    import getuser
from liblo      import Address, AddressError, send, Server, ServerError
from sys        import exit
from pathlib    import Path
from os.path    import isfile
from os         import (
        getpid  , access    , W_OK  ,
        )
from logging    import (
        FileHandler , StreamHandler , Formatter , getLogger ,
        DEBUG       , INFO          , WARNING   , ERROR     , CRITICAL  ,
        )



'''
ToDo:
    * Add a command and control OSC Server for issuing commands to oscwhipsers using OSC messages
    * Add logging
        - Needs to be a class
        - Instantiate in oscwhispers.py
        - Pass into all other instatianted objects (ConfigFile, OTWFiles, etc... )
        - Logger class needs a method for adding a log
'''

class Logger:
    """ 
        Setup logging 
    """

    # Class variables and CONSTANTS
    LOG_NAME        = "OSC Whispers log"
    LOG_DIR         = "/var/log/osctoolkit/"
    LOG_DIR_LOCAL   = "/home/" + getuser() + "/.osctoolkit/log/"
    LOG_FILE        = "oscwhispers.log"
    LOG_FORMAT      = "%(asctime)s %(levelname)s - %(message)s"
    
    # Find log location with write permisions
    if access( LOG_DIR , W_OK ):
        logDir      = LOG_DIR
    else:
        logDir      = LOG_DIR_LOCAL
        Path( logDir ).mkdir( parents = True , exist_ok = True )

    def __init__(
            self                    ,
            debugMode   = bool()    ,
            ):
        """
            Initialization of logging
        """
        # Create logger
        self.logger = getLogger( self.LOG_NAME )
        if debugMode:
            self.logger.setLevel( DEBUG )
        else:
            self.logger.setLevel( INFO )

        # Create stream and file handler
        self.streamHandler  = StreamHandler()
        self.fileHandler    = FileHandler( self.logDir + self.LOG_FILE )

        # Set Log levels
        self.streamHandler.setLevel( WARNING )
        if debugMode:
            self.fileHandler.setLevel( DEBUG )
        else:
            self.fileHandler.setLevel( INFO )

        # Create and set log formatter
        self.formatter  = Formatter( self.LOG_FORMAT )
        self.streamHandler.setFormatter( self.formatter )
        self.fileHandler.setFormatter( self.formatter )

        # Add handlers to the logger
        self.logger.addHandler( self.streamHandler )
        self.logger.addHandler( self.fileHandler )


    def log(
            self            ,
            level   = int() ,
            message = str() ,
            ):
        """
            Create a log entry

            Log Levels:
                0   - Debug
                1   - Info
                2   - Warning
                3   - Errori
                4   - Critical

      
            Guide (from Python logging documentation):
                DEBUG 	    Detailed information, typically of interest only when 
                            diagnosing problems.
                
                INFO 	    Confirmation that things are working as expected.
                
                WARNING     An indication that something unexpected happened, or 
                            indicative of some problem in the near future (e.g. ‘disk space low’). 
                            The software is still working as expected.
                
                ERROR 	    Due to a more serious problem, the software has not been 
                            able to perform some function.

                CRITICAL    A serious error, indicating that the program itself may be 
                            unable to continue running.
        """
        # Maybe create a logger error to raise if value < 0 or > 4, and log it critical
        self.logLevels  = {
                0   : "debug"       ,
                1   : "info"        ,
                2   : "warning"     ,
                3   : "error"       ,
                4   : "critical"    ,
                }
        exec(
                "self.logger." + self.logLevels[ level ] + "(\"" + message + "\")"
                )


## Load config file and parse arguments
class ConfigFile:
    """ Load and parse OSC Toolkit configuration file for OSC Whispers. """

    ## Class variables for configuration file parsing
    # Declare configuration file contants
    CONFIG_PROPERTY_ARG     = 0
    CONFIG_VALUE_ARG        = 1
    CONFIG_PROTO_COMMENT    = 0 
    CONFIG_COMMENT_SYMBOL   = '#' 

    def __init__(
            self                , 
            configFileLocations ,
            logger              ,
            ):
        """ Initialization procedure for ConfigFile. """

        # Declare config arguments with default values defaults
        self.serverListenPort       = 9000
        self.daemonFiles            = []

        # Set up logger
        self.logger = logger

        # Run initialization fucntions
        self.configData = self.parseConfigFile(
                self.loadConfigFile( configFileLocations )
                )

    def loadConfigFile(
            self                , 
            configFileLocations ,
            ):
        """ Load the configuration file. """

        ## Load config file
        #  Rebuild and use 'with ... as ... '
        for checkConf in configFileLocations:
            if isfile( checkConf ):
                configFileLocation = checkConf
                break
        configFile  = open( configFileLocation, 'r' )
        configLines = configFile.read().split( '\n' )
        configFile.close()
        return configLines

    def parseConfigFile(
            self        , 
            configLines ,
            ):
        # Parse config file lines
        for lineRead in configLines:
            if lineRead:
                # Seperate the data in each line by whitespace
                lineData = lineRead.split( self.CONFIG_COMMENT_SYMBOL )[ self.CONFIG_PROTO_COMMENT ].split( ' ' )
                
                # OSC Settings
                if lineData[ self.CONFIG_PROPERTY_ARG ] == 'oscwhispers.server_listen_port':
                    self.serverListenPort = int(
                            lineData[ self.CONFIG_VALUE_ARG ]
                            )

                # Daemon OTW files
                if lineData[ self.CONFIG_PROPERTY_ARG ] == 'oscwhispers.daemon_file':
                    self.daemonFiles.append(
                            lineData[ self.CONFIG_VALUE_ARG ]
                            )

        
        return {
                'serverListenPort'          : self.serverListenPort         ,
                'daemonFiles'               : self.daemonFiles              ,
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
    '''
    
    def __init__(
            self        , 
            configData  ,
            logger      ,
            ):
        # Declare argument variables with default values
        self.daemonFiles            = configData[ 'daemonFiles' ]
        self.otwFileLocations       = []

        self.pidDir = "/tmp"
        self.pid    = str(
                getpid()
                )

        # Set up logger
        self.logger = logger

        # Run initilization functions
        self.argData = self.parse()


    def parse( self ):
        parser = ArgumentParser(
                description = 'An Open Sound Control forwarding agent.' ,
                )
        
         ## Add arguments
        
        # OTW File(s)
        otwFileGroup = parser.add_mutually_exclusive_group( required = True )

        otwFileGroup.add_argument(
                '-f'                                                                , 
                '--file'                                                            , 
                dest    = 'otw'                                                     , 
                nargs   = '+'                                                       , 
                help    = 'Specifies OTW files to be loaded into OSC Whispers.'     ,
                )

        # Daemon Mode, load files from config file, create pid file in tmp
        otwFileGroup.add_argument(
                '-d'                                    ,
                '--daemon'                              ,
                dest        = 'daemon'                  ,
                action      = 'store_true'              ,
                help        = 'Start in daemon mode.'   ,
                )
   
        # Set argument values
        args = parser.parse_args()

        # Load and parse otw files passed as arguments
        if args.otw:
            # Load OTW Files into a list for the argData dictionary
            for arg in args.otw:
                self.otwFileLocations.append( arg )
        elif args.daemon:
            # Started up in daemon mode, load otw file locations from config file
            for daemonFile in self.daemonFiles:
                self.otwFileLocations.append( daemonFile )
            # Create PID
            with open( self.pidDir + "/oscwhispers.pid" , "w" ) as self.pidFile:
                self.pidFile.write( self.pid )
    
        return {
                'otwFileLocations'          : self.otwFileLocations         ,
                }



class OTWFiles:
    """
    This class takes a list of OTW File locations and parses the data into an
    OSC Client list and a forwarding ruleset.
    """
    
    # Declare OTWFiles() class variables
    OTW_PROTO_COMMENT               = 0
    OTW_COMMENT_SYMBOL              = '#'
    OTW_PATH_SYMBOL                 = '/'
    OTW_PORT_SYMBOL                 = ':'
    OTW_NO_PATH_REPLACEMENT_LENGTH  = 1
    
    PATH_PREFIX_INDEX           = 0
    TRUNCATE_INDICATOR_INDEX    = 1
    TARGETS_START_INDEX         = 2

    OSC_TARGETS_ID_INDEX        = 0
    OSC_TARGETS_TARGET_INDEX    = 1

    # These indexes refer to data inside of oscTargets
    OSC_TARGET_IP_INDEX                 = 0
    OSC_TARGET_PORT_INDEX               = 1
    OSC_TARGET_PATH_REPLACEMENT_INDEX   = 2
    
    # Used for splitting path aliases from ports
    OSC_TARGET_PORT_SPLIT_PORT_INDEX                    = 0
    OSC_TARGET_PORT_SPLIT_PATH_REPLACEMENT_START_INDEX  = 1

    
    
    def __init__(
            self        , 
            otwFiles    ,
            logger      ,
            ):
        # Declare variables for instatiated object
        oscClients = []

        # Setup the logger
        self.logger = logger

        # Run initialization functions
        self.otwFileData = self.parseOtwFiles(
                self.loadOtwFiles( otwFiles )
                )


    def loadOtwFiles(
            self        , 
            otwFiles    ,
            ):
        """ Load the forwarding destinations from file. """
        # OTW file constants
        # rebuild using 'with ... as ...'
    
        # run for loop through all args.otw entries
        otwLines = []
        for otwFileName in otwFiles:
            # File load vars
            with open( otwFileName, 'r' ) as otwFile:
                otwLines += otwFile.read().split( '\n' )
        return otwLines

    
    
    def buildOSCPath(self, pathElements = [] ):
        """ Take a list of path elements (directory names) and return a string representing an OSC path """
        oscPath = ''
        for element in pathElements:
            oscPath += '/' + element
        return oscPath
    


    def oscTargetData(self, target = '' ):
        """ Take an osc target 'IP:PORT(/Path/Replacement) and return a  list of osc target data for each target. """
        # Used to parse target information
        OTW_PATH_SYMBOL                 = '/'
        OTW_PORT_SYMBOL                 = ':'
        OTW_NO_PATH_REPLACEMENT_LENGTH  = 1

        # Used for splitting path aliases from ports
        OSC_TARGET_PORT_SPLIT_PORT_INDEX                    = 0
        OSC_TARGET_PORT_SPLIT_PATH_REPLACEMENT_START_INDEX  = 1

        # These indexes refer to data inside of oscTargets
        OSC_TARGET_IP_INDEX                 = 0
        OSC_TARGET_PORT_INDEX               = 1
        OSC_TARGET_PATH_REPLACEMENT_INDEX   = 2

        # Get ip
        ip = target.split( OTW_PORT_SYMBOL )[ OSC_TARGET_IP_INDEX ]
        
        # Determine if there is a path alias

        if len(
                target.split( OTW_PATH_SYMBOL )
                ) == OTW_NO_PATH_REPLACEMENT_LENGTH:
                
            # There is no path alias
            port    = target.split( OTW_PORT_SYMBOL )[ OSC_TARGET_PORT_INDEX ]
            alias   = None

        else:
            # There is a path alias
            port = target.split(
                    OTW_PORT_SYMBOL
                    )[ OSC_TARGET_PORT_INDEX ].split(
                            OTW_PATH_SYMBOL
                            )[ OSC_TARGET_PORT_SPLIT_PORT_INDEX ]

            alias = self.buildOSCPath(
                    target.split(
                        OTW_PORT_SYMBOL
                        )[ OSC_TARGET_PORT_INDEX ].split(
                            OTW_PATH_SYMBOL
                            )[ OSC_TARGET_PORT_SPLIT_PATH_REPLACEMENT_START_INDEX: ]
                        )

        return [
            ip      ,
            port    ,
            alias   ,
            ]

    
    
    def parseOtwFiles(
            self        , 
            otwLines    ,
            ):
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
        oscTargets      = []
        allOscTargets   = [] 
        preIdOscTargets = []
        
        for lineRead in otwLines:
            if lineRead: 
                # Seperate the data in each line by whitespace and ignore data post comment symbol
                lineData = lineRead.split( self.OTW_COMMENT_SYMBOL )[ self.OTW_PROTO_COMMENT ].split()
                if lineData:

                    # Iterate through the OSC tagets for the forwarding rule
                    for dataIndex in range(
                            self.TARGETS_START_INDEX , 
                            len( lineData )
                            ):

                        # Debug print oscTargetData
                        allOscTargets.append(
                                self.oscTargetData(
                                    lineData[ dataIndex ]
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
                                preIdOscTargets.append( target )

        # Enumerate preIdOscTargets and append the value and iteration number to oscTargets
        for target in enumerate( preIdOscTargets ):
            oscTargets.append(
                    [
                        target[ ENUMERATE_ITERATE_INDEX ]   , 
                        target[ ENUMERATE_VALUE_INDEX ]     ,
                        ]
                    )
        
        
        ## Build forwarding rules list
        forwardingRules = []
        pathPrefixRules = []
        
        for lineRead in otwLines:
            if lineRead: 
                # Seperate the data in each line by whitespace
                lineData = lineRead.split( self.OTW_COMMENT_SYMBOL )[ self.OTW_PROTO_COMMENT ].split()
                if lineData:

                    #parse forwarding destinations line
                    forwardingPathPrefix = lineData[ self.PATH_PREFIX_INDEX ].strip( '/' )

                    # Determine the truncation indicator boolean
                    if lineData[ self.TRUNCATE_INDICATOR_INDEX ] == "+":
                        #do not truncate prefix of path
                        truncatePathPrefix = False
                    elif lineData[ self.TRUNCATE_INDICATOR_INDEX ] == "-":
                        #truncate prefix of path
                        truncatePathPrefix = True
                    else:
                        # Raise better exceptions
                        print(
                                'Error: OTW file '                          + 
                                otwFileName                                 + 
                                ' contains incorrect truncation indicator'
                                )
                        exit( ERROR )

                    
                    
                    # Check all targets in OTW File agains oscTargets and store ID list
                    idList = []

                    '''
                        When checking for the ID of the target Path alias must also be checked
                    '''
                    
                    for dataIndex in range(
                            self.TARGETS_START_INDEX    , 
                            len( lineData )             ,
                            ):


                        for target in oscTargets:
                            if self.oscTargetData(
                                    lineData[dataIndex]
                                    ) == target[ self.OSC_TARGETS_TARGET_INDEX ]:
                                idList.append(
                                        target[ self.OSC_TARGETS_ID_INDEX ] 
                                        )


                    # Finally, build the forwarding rule list
                    forwardingRules.append(
                            [
                                forwardingPathPrefix    , 
                                truncatePathPrefix      , 
                                idList                  ,
                                ]
                            )

        # Decode the rules, and log as info here

        return {
                'forwardingRules'   : forwardingRules   ,
                'oscTargets'        : oscTargets        ,
                }



### Create functions 
class OSC:
    """This class contains all functions for Open Sound Control operations"""
    
    # Declare OSC class constants and variables
    MAIN_LOOP_LATENCY   = 1

    IP_INDEX                = 0
    PORT_INDEX              = 1
    PATH_REPLACEMENT_INDEX  = 2

    CLIENT_ID_INDEX = 0
    TARGET_INDEX    = 1

    PATH_PREFIX_INDEX           = 0
    TRUNCATION_INDICATOR_INDEX  = 1
    CLIENT_TARGET_LIST_INDEX    = 2

    PATH_PREFIX_SPLIT_INDEX = 1

    
    
    def __init__(
            self                , 
            serverListenPort    , 
            forwardingRules     , 
            oscTargets          ,
            logger              ,
            ):
        # Declare instatiation variables
        self.forwardingRules = forwardingRules

        # Set up logger
        self.logger = logger

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
        self.listenServer = self.setupOscServer( serverListenPort )

        # Setup the OSC clients
        self.oscClients = self.setupOscClients( oscTargets )


    
    def sendOSC(
            self    , 
            target  , 
            path    , 
            args    ,
            ):
        #send osc messages in this function
        libloSend = 'send(target, path'
        for eachArg in enumerate( args ):
            libloSend += ', args[' + str(
                    eachArg[ ENUMERATE_ITERATE_INDEX ]
                    )+']'
        libloSend+=')'
        exec( libloSend )
        return



    def forwardMessage(
            self    , 
            path    , 
            args    ,
            ):
        """ Forward the osc Message based on forwarding rules. """
        # This is a special function called as a liblo method (add_method) 

        # Check message against the forwarding rules
        for rule in self.forwardingRules:
            
            # Check the path prefix against the forwarding rules
            if rule[ self.PATH_PREFIX_INDEX ] == self.pathPrefix( path ):

                
                # Check if the matching rule has a truncation indicator
                if rule[ self.TRUNCATION_INDICATOR_INDEX ]:
                    # Truncaton indicator

                    for client in rule[ self.CLIENT_TARGET_LIST_INDEX ]:

                        clientPathReplacement = self.oscTargets[ client ][ self.PATH_REPLACEMENT_INDEX ]
                        if clientPathReplacement:
                            # Replace the path
                            self.sendOSC(
                                    self.oscClients[ client ]   , 
                                    clientPathReplacement       , 
                                    args                        ,
                                    )
                        else:
                            self.sendOSC(
                                    self.oscClients[ client ]       , 
                                    self.truncatePathPrefix( path ) , 
                                    args                            ,
                                    )

                else:

                    for client in rule[ self.CLIENT_TARGET_LIST_INDEX ]:
                        clientPathReplacement = self.oscTargets[ client ][ self.PATH_REPLACEMENT_INDEX ]
                        if clientPathReplacement:
                            # Replace the path
                            self.sendOSC(
                                    self.oscClients[ client ]   , 
                                    clientPathReplacement       , 
                                    args                        ,
                                    )
                        else:
                            self.sendOSC(
                                    self.oscClients[ client ]   , 
                                    path                        , 
                                    args                        ,
                                    )
        return



    def setupOscServer(
            self                , 
            serverListenPort    ,
            ):
        #setup OSC Server
        try:
            oscListenServer = Server( serverListenPort )
            
            #register OSC Listen method
            oscListenServer.add_method(
                    None                , 
                    None                , 
                    self.forwardMessage ,
                    )

        except ServerError as error:
            exit( error )
        return oscListenServer



    def setupOscClients(
            self                , 
            oscMessageTargets   ,
            ):
        #Create OSC clients from a list of targets
        oscClients = []
        for target in oscMessageTargets:
            try:
                oscClients.append(
                        Address(
                            target[ OTWFiles.OSC_TARGETS_TARGET_INDEX ][ self.IP_INDEX ]    , 
                            target[ OTWFiles.OSC_TARGETS_TARGET_INDEX ][ self.PORT_INDEX ]  ,
                            )
                        )
            except AddressError as error:
                exit( error )
        return oscClients



    def truncatePathPrefix(
            self    , 
            inPath  ,
            ):
        # Remove a paths top level
        STARTING_NON_PATH_PREFIX_INDEX  = 2
        outPath                         = ''
        for dirs in range(
                STARTING_NON_PATH_PREFIX_INDEX  , 
                len(
                    inPath.split( '/' )
                    )
                ):
            outPath += '/' + inPath.split( '/' )[ dirs ]
        return outPath



    def pathPrefix(
            self    , 
            inpath  ,
            ):
        # Return the a paths top level
        prefix = inpath.split( '/' )[ self.PATH_PREFIX_SPLIT_INDEX ]
        return prefix
