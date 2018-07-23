#!/usr/bin/python3
"""
OSC Shout
  oscshout.py

    Written By: Shane Hutter
    
    Required Dependencies:  python >= 3.5, pyliblo

      This python script, and all of OSC_Tools is licensed
      under the GNU GPL version 3

      The OSC Shout module contains all of the functions and classes required
      to run OSC Shout

      OSC Shout is a part of osctoolkit

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
from liblo      import Address, AddressError, send
from sys        import exit
from os.path    import isfile



class ParseArgs():
    """Parse command line arguments"""


    def __init__( self ):

        # Argument parsing variables
        self.oscPathElements    = []
        self.oscTargetPath      = ''
        self.targetIp           = ''
        self.targetPort         = ''
        self.oscArgList         = []

        # Run intitialization methods
        self.argData = self.parse()

    def parse( self ):
        # Argument parsing constant
        TARGET_ARG_INDEX        = 0
        IP_PORT_PATH_ARG_INDEX  = 1
        IP_PORT_PATH_INDEX      = 0
        IP_INDEX                = 0
        PORT_PATH_INDEX         = 1
        PORT_INDEX              = 0
        TOP_LEVEL_PATH_INDEX    = 1

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
        parser.add_argument(
                "target"                            , 
                nargs   = 1                         , 
                help    = "IP:PORT/Path/to/message" ,
                )
            
        # OSC messages
        parser.add_argument(
                "message"                                                                                   , 
                nargs       = "+"                                                                           , 
                help        = "Strings, integers, and floating point values to be sent in the OSC message." ,
                )
        
        args = parser.parse_args()

        ## Gather ip, port, and path from args.target
        oscIpPortPath = args.target[ TARGET_ARG_INDEX ]

        # Store target IP address
        self.oscTargetIp = oscIpPortPath.split( ':' )[ IP_INDEX ]

        # Store target port number
        self.oscTargetPort = int(
                oscIpPortPath.split( ':' )[ PORT_PATH_INDEX ].split( '/' )[ PORT_INDEX ]
                )

        # Store OSC message path
        oscPathElements = []
        for pathElement in enumerate(
                oscIpPortPath.split( ':' )[ PORT_PATH_INDEX ].split( '/' )
                ):
            if pathElement[ ENUMERATE_ITERATE_INDEX ] >= TOP_LEVEL_PATH_INDEX:
                oscPathElements.append(
                        pathElement[ ENUMERATE_VALUE_INDEX ]
                        )
        for pathElement in oscPathElements:    
            self.oscTargetPath += '/' + pathElement

        # Gather oscArgList from args.message and convert to an integer, floating point, or string
        for oscArg in args.message:
            # If the message is surrounded by " or ' then do not convert from a string
            try:
                # Conver to an integer
                self.oscArgList.append(
                        int( oscArg )
                        )
            except:
                try:
                    # Convert to a floating point value
                    self.oscArgList.append(
                            float( oscArg )
                            )
                except:
                    # Keep as a string
                    self.oscArgList.append(
                            str( oscArg )
                            )
        return {
                'oscTargetIp'   : self.oscTargetIp      ,
                'oscTargetPort' : self.oscTargetPort    ,
                'oscTargetPath' : self.oscTargetPath    ,
                'oscArgList'    : self.oscArgList       ,
                }


def sendOSC(
        target      , 
        path        , 
        messages    ,
        ):
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
    for eachMessage in enumerate( messages ):
        libloSend += ', messages[' + str(
                eachMessage[ ENUMERATE_ITERATE_INDEX ]
                ) + ']'
    libloSend += ')'
    exec( libloSend )
    return


def createOSCClient(
        oscTargetIp     , 
        oscTargetPort   ,
        ):
    # Create OSC Client
    try:
        return Address(
                oscTargetIp     , 
                oscTargetPort   ,
                )
    except AddressError as error:
        exit( error )
