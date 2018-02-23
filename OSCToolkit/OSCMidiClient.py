#!/usr/bin/env python3
"""
OSC Midi Client
    OSCMidiClient.py

    Written by: Shane Hutter

    Required Dependencies:  python >= 3.5, pyliblo, mido, rtmidi

      The OSC Midi Client module contains all the functions and classes 
      required to run OSC Midi Client

      OSC Midi Client is a part of osctoolkit

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

# Import Modules
from . import *
from argparse import ArgumentParser
from liblo import Address, AddressError, send
from mido import open_input, open_output, Parser
from sys import exit
from os.path import isfile



'''
Config and Args:
    * listen port
    * command listen port
    * osc target
    * default virtual midi port [name, name, name]
    * default midi device [device name, device name, etc...]
    * Verbosity
        * verbose virtual midi ports
        * verbose midi devices
        * verbose listen port
        * verbose command port
        * verbose osc target
        * verbose midi data

Args:
    * list midi device names (mido)
    * listen to midi device (device name)
    * create virtual midi port [name, name, name]
        * /oscmidi/name/(midi channel number)
    * Verbosity
        * Quite mode
        * Specific verbosity
        * Specific quiet
'''


class ConfigFile:
    """Load and parse OSC Toolkit configuration file for OSC Midi Client"""

    ## Class variables for configuration file parsing
    # Declare configuration file contants
    CONFIG_PROPERTY_INDEX = 0
    CONFIG_VALUE_INDEX = 1
    CONFIG_PROTO_COMMENT_INDEX = 0 
    CONFIG_COMMENT_SYMBOL = '#'
    CONFIG_PROPERTY_PREFIX = 'oscmidi-client'

    def __init__(self, configFileLocations):

        ## Declare config arguments with default values defaults
        # Verbosity settings
        self.verboseVirtualMidiPorts = False
        self.verboseMidiDevices = False
        self.verboseListenPort = False
        self.verboseCommandPort = False
        self.verboseOscTarget = False
        self.verboseMidiData = False

        # OSC Port settings
        self.oscServerListenPort = 9010
        self.oscServerCommandPort = 9011

        # Midi ports and devices
        self.midiVirtualPorts = []
        self.midiDevices = []

        # Run initialization fucntions
        self.configData = self.parseConfigFile(
                self.loadConfigFile(
                    configFileLocations
                    ))

    def loadConfigFile(self, configFileLocations):
        ## Load config file
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
                lineData = lineRead.split(self.CONFIG_COMMENT_SYMBOL)[self.CONFIG_PROTO_COMMENT_INDEX].split(' ')

                # Verbosity settings
                if lineData[self.CONFIG_PROPERTY_INDEX] == self.CONFIG_PROPERTY_PREFIX + '.verbose_virtual_midi_ports':
                    self.verboseVirtualMidiPorts = bool(
                            int(
                                lineData[self.CONFIG_VALUE_INDEX]
                                )
                            )

                if lineData[self.CONFIG_PROPERTY_INDEX] == self.CONFIG_PROPERTY_PREFIX + '.verbose_midi_devices':
                    self.verboseMidiDevices = bool(
                            int(
                                lineData[self.CONFIG_VALUE_INDEX]
                                )
                            )

                if lineData[self.CONFIG_PROPERTY_INDEX] == self.CONFIG_PROPERTY_PREFIX + '.verbose_listen_port':
                    self.verboseListenPort = bool(
                            int(
                                lineData[self.CONFIG_VALUE_INDEX]
                                )
                            )

                if lineData[self.CONFIG_PROPERTY_INDEX] == self.CONFIG_PROPERTY_PREFIX + '.verbose_command_port':
                    self.verboseCommandPort = bool(
                            int(
                                lineData[self.CONFIG_VALUE_INDEX]
                                )
                            )

                if lineData[self.CONFIG_PROPERTY_INDEX] == self.CONFIG_PROPERTY_PREFIX + '.verbose_osc_target':
                    self.verboseOscTarget = bool(
                            int(
                                lineData[self.CONFIG_VALUE_INDEX]
                                )
                            )

                if lineData[self.CONFIG_PROPERTY_INDEX] == self.CONFIG_PROPERTY_PREFIX + '.verbose_midi_data':
                    self.verboseMidiData = bool(
                            int(
                                lineData[self.CONFIG_VALUE_INDEX]
                                )
                            )

                # OSC Settings
                if lineData[self.CONFIG_PROPERTY_INDEX] == self.CONFIG_PROPERTY_PREFIX + '.osc_server_listenPort':
                    self.oscServerListenPort = int(
                            lineData[
                                self.CONFIG_VALUE_INDEX
                                ]
                            )

                if lineData[self.CONFIG_PROPERTY_INDEX] == self.CONFIG_PROPERTY_PREFIX + '.osc_server_command_port':
                    self.oscServerCommandPort = int(
                            lineData[
                                self.CONFIG_VALUE_INDEX
                                ]
                            )




                # MIDI Settings
                if lineData[self.CONFIG_PROPERTY_INDEX] == self.CONFIG_PROPERTY_PREFIX + '.midi_virtual_ports':
                    for data in enumerate(lineData):
                        if data[ENUMERATE_ITERATE_INDEX] > self.CONFIG_PROPERTY_INDEX:
                            self.midiVirtualPorts.append(
                                    data[
                                        ENUMERATE_VALUE_INDEX
                                        ]
                                    )

                if lineData[self.CONFIG_PROPERTY_INDEX] == self.CONFIG_PROPERTY_PREFIX + '.midi_devices':
                    for data in enumerate(lineData):
                        if data[ENUMERATE_ITERATE_INDEX] > self.CONFIG_PROPERTY_INDEX:
                            self.midiDevices.append(
                                    data[
                                        ENUMERATE_VALUE_INDEX
                                        ]
                                    )


                '''
                ENUMERATE_ITERATE_INDEX = 0
                ENUMERATE_VALUE_INDEX = 1
                '''




        return {
                'verboseVirtualMidiPorts': self.verboseVirtualMidiPorts,
                'verboseMidiDevices': self.verboseMidiDevices,
                'verboseListenPort': self.verboseListenPort,
                'verboseCommandPort': self.verboseCommandPort,
                'verboseOscTarget': self.verboseOscTarget,
                'verboseMidiData': self.verboseMidiData,
                'oscServerListenPort': self.oscServerListenPort,
                'oscSeverCommandPort': self.oscServerCommandPort,
                'midiVirtualPorts': self.midiVirtualPorts,
                'midiDevices': self.midiDevices,
                }



#class ParseArgs:
#    """Parse command line arguments for OSC Midi Client"""


