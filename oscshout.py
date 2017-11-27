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
from liblo import Address, AddressError, send
from sys import exit


#Global enumeration indicies constants
ENUMERATE_ITERATE_INDEX = 0
ENUMERATE_VALUE_INDEX = 1


if __name__ == "__main__":
    ## Parse Arguments
    parser = ArgumentParser()

    # Argument parsing constant
    TARGET_ARG_INDEX = 0
    IP_PORT_PATH_ARG_INDEX = 1
    IP_PORT_PATH_INDEX = 0
    IP_INDEX = 0
    PORT_PATH_INDEX = 1
    PORT_INDEX = 0
    TOP_LEVEL_PATH_INDEX = 1

    # Argument parsing variables
    oscPathElements = []
    oscTargetPath = ''
    oscArgList = []

    ## Add Arguments
    '''
        The first argument will be an IPv4 address, target port number, and the OSC message path name
            i.e.    127.0.0.1:9999/foo/bar

        All following arguments will be converted into a string, integer, or floating point value,
        then sent in the OSC message.
    '''
    parser.add_argument("target", nargs=1, help="IP:PORT/Path/to/message")
    parser.add_argument("message", nargs="+", help="Strings, integers, and floating point values to be sent in the OSC message.")
    
    args = parser.parse_args()

    ## Gather ip, port, and path from args.target
    oscIpPortPath = args.target[TARGET_ARG_INDEX]
    
    # Store target IP address
    oscTargetIp = oscIpPortPath.split(':')[IP_INDEX]

    # Store target port number
    oscTargetPort = int(oscIpPortPath.split(':')[PORT_PATH_INDEX].split('/')[PORT_INDEX])

    # Store OSC message path
    for pathElement in enumerate(oscIpPortPath.split(':')[PORT_PATH_INDEX].split('/')):
        if pathElement[ENUMERATE_ITERATE_INDEX] >= TOP_LEVEL_PATH_INDEX:
            oscPathElements.append(pathElement[ENUMERATE_VALUE_INDEX])
    for pathElement in oscPathElements:    
        oscTargetPath += '/' + pathElement
                
    # Gather oscArgList from args.message and convert to an integer, floating point, or string
    for oscArg in args.message:
        try:
            # Conver to an integer
            oscArgList.append(int(oscArg))
        except:
            try:
                # Convert to a floating point value
                oscArgList.append(float(oscArg))
            except:
                # Keep as a string
                oscArgList.append(str(oscArg))


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


def createOSCClient():
    # Create OSC Client
    try:
        global oscTarget
        oscTarget = Address(oscTargetIp, oscTargetPort)
    except AddressError as error:
        exit(error)


if __name__ == "__main__":
    createOSCClient()
    sendOSC(oscTarget, oscTargetPath, oscArgList)
