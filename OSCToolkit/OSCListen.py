#!/usr/bin/python3
"""
OSC Listen
  OSCListen.py
    
    Written by: Shane Hutter

    Required Dependencies:  python >= 3.5, pyliblo
      
      The OSC Listen module contains all of the functions and classes for OSC Listen

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
"""

# Import modules
from .          import *
from argparse   import ArgumentParser
from liblo      import Server, ServerError
from sys        import exit
from os.path    import isfile


# Declare class variables
exitCall = False
oscListenServers = []

class ConfigFile():
    """Load and parse OSC Toolkit configuration file for OSC Listen."""
    ## Class variables for loading and parsing the configuration file
    # Declare config constants
    CONFIG_PROPERTY_ARG = 0
    CONFIG_VALUE_ARG = 1
    CONFIG_PROTO_COMMENT = 0
    CONFIG_COMMENT_SYMBOL = '#'
        
    
    def __init__(
            self                , 
            configFileLocations ,
            ):
        """ Initialization steps for new object.  """
        # config variabless with default values
        self.verboseListenPorts = False
        self.verboseMotd = False
        self.listenPorts = []
        self.motd = ''
    
        # Run initialization functions
        self.configData = self.parseConfigFile(
                self.loadConfigFile( configFileLocations )
                )
        
    def loadConfigFile(
            self                , 
            configFileLocations ,
            ):
        """ Load the configuration file and return its contents in lines. """

        ## Check for configuration file location
        for checkConf in configFileLocations:
            if isfile( checkConf ):
                configFileLocation = checkConf
                break

        ## Load the configuration file and parse into lines
        with open(
                configFileLocation  ,
                'r'                 ,
                ) as configFile:
            configFileLines = configFile.read().split( '\n' )

        return configFileLines
   


    def parseConfigFile(
            self        , 
            configLines ,
            ):
        """ Parse the configuration file and return a dictionary of values. """
        # Parse config file lines
        for lineRead in configLines:
            if lineRead:

                # Seperatre lines by whitespace
                lineReadProtoComment = lineRead.split(
                        self.CONFIG_COMMENT_SYMBOL
                        )[ self.CONFIG_PROTO_COMMENT ].split(' ')

                ## Verbosity Settings
                # Verbose listen ports
                if lineReadProtoComment[ self.CONFIG_PROPERTY_ARG ] == 'osclisten.verbose_listen_ports':
                    self.verboseListenPorts = bool(
                            int(
                                lineReadProtoComment[ self.CONFIG_VALUE_ARG ]
                                )
                            )
                    
                # Verbose Message of the Day
                if lineReadProtoComment[ self.CONFIG_PROPERTY_ARG ] == 'osclisten.verbose_motd':
                    self.verboseMotd = bool(
                            int(
                                lineReadProtoComment[ self.CONFIG_VALUE_ARG ]
                                )
                            )

                ## Message of the Day
                if lineReadProtoComment[ self.CONFIG_PROPERTY_ARG ] == 'osclisten.motd':
                    for configArg in range(
                            self.CONFIG_VALUE_ARG       , 
                            len( lineReadProtoComment ) ,
                            ):
                        self.motd += lineReadProtoComment[ configArg ] + ' '
            
                ## OSC Settings
                # Listen port
                if lineReadProtoComment[ self.CONFIG_PROPERTY_ARG ] == 'osclisten.listen_port':
                    self.listenPorts.append(
                            int(
                                lineReadProtoComment[ self.CONFIG_VALUE_ARG ]
                                )
                            )

        return {
                'verboseListenPorts'    : self.verboseListenPorts   , 
                'listenPorts'           : self.listenPorts          ,
                'verboseMotd'           : self.verboseMotd          , 
                'motd'                  : self.motd                 ,
                }



class ParseArgs():
    """ Parse command line arguments for OSC Listen. """

    def __init__(
            self        , 
            configData  ,
            ):
        """ Initilization process for newly instantiated classes. """
        # argument vars with default values
        self.verboseListenPorts = configData[ 'verboseListenPorts' ]
        self.verboseMotd = configData[ 'verboseMotd' ]
        self.listenPorts = []

        # run initilization methods
        self.argData = self.parse()

    def parse( self ):
        ## Parse Arguments
        # These values may potentially overwrite config arguments
        parser = ArgumentParser(
                description = 'Display incoming Open Sound Control messages.'   ,
                )

        ## Add arguments
        # List additional listen ports
        parser.add_argument(
                "-l"                                                                    ,
                "--listen"                                                              , 
                dest        = "ports"                                                   , 
                nargs       = "+"                                                       , 
                type        = int                                                       , 
                help        = "List additional ports to listen for OSC messages on."    ,
                )

        # Verbosely display listen ports
        parser.add_argument(
                "-v"                                                                , 
                "--verbose"                                                         , 
                action      = "store_true"                                          , 
                help        = "Verbosely display listen ports and MOTD on startup." ,
                )

        # Add specific verbosity for listen ports and MOTD (see as OSC Whispers arg parsing)
        # Add quiet mode to halt verbosity
        # Add specific quiet mode (see OSC Whispers arg parsing)

        # Set argument vars
        args = parser.parse_args()
        if args.verbose:
            self.verboseListenPorts = self.verboseMotd = args.verbose
        if args.ports:
            for port in args.ports:
                self.listenPorts.append( port )
        
        return {
                'verboseListenPorts'    : self.verboseListenPorts   ,
                'verboseMotd'           : self.verboseMotd          , 
                'listenPorts'           : self.listenPorts          ,
                }
        
    
# Verbosely display listen ports
def displayListenPorts( listenPorts ):
    for portIdNum in listenPorts:
        print(
                'Listening for OSC on port number: '    , 
                end = ''                                ,
                )
        print( portIdNum )
    print()
    return
            
    
# Setup listen ports
def setupOSCServers( listenPorts ):
    try:
        for oscServerId in listenPorts:
            oscListenServers.append(
                    Server( oscServerId )
                    )
    except ServerError as  error:
        exit( error )
    return


# Build the functions for echoing messages on each port, then regiter as OSC servers
def buildOSCServers( listenPorts ):
    # Setup Constants for building OSC servers
    global EXIT_ARG_INDEX  # ToDo: Fix this global!!!
    EXIT_ARG_INDEX      = 0
    COMMAND_OSC_PATH    = '/osclisten'
    EXIT_COMMAND_PATH   = COMMAND_OSC_PATH + '/exit'

    # Setup variables for building the OSC servers
    oscSppDef           = []
    oscSppRegistration  = []

    # Build server per port (spp) fucntion strings
    for eachPort in listenPorts:
        oscSppDefLine = 'def oscServer_' + str( eachPort ) + '(path, args):\n'
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
        oscSppDefLine += '        exit()\n'
        oscSppDefLine += '    else:\n'
        # or else echo the incoming message
        oscSppDefLine += '        print("' + str( eachPort ) + ': ", end = "")\n'
        oscSppDefLine += '        print(path, end = " ")\n'
        oscSppDefLine += '        print(args)\n'
        oscSppDefLine += '    return'
        oscSppDef.append( oscSppDefLine )

    # Build server per port (spp) functions
    for execSppDefLine in oscSppDef:
        exec( execSppDefLine )

    # Build server per port (spp) OSC method registration string
    for eachPort in listenPorts:
        oscSppBuild = 'oscListenServers[eachMethod[ENUMERATE_ITERATE_INDEX]].add_method(None, None, oscServer_' + str( eachPort ) + ')'
        oscSppRegistration.append( oscSppBuild )
    
    # Register methods for listening on each port as an OSC Server
    for eachMethod in enumerate( oscSppRegistration ):
        exec(
                eachMethod[ ENUMERATE_VALUE_INDEX ]
                )
    return

def displayMOTD( motd ):
    # MOTD variables
    # Set this in config, and maybe on the fly with an argument
    print( motd )
    print()
    return
