#!/usr/bin/env python
'''
OSC Whispers
    oscwhispers.py
      Written by: Shane Huter

    Required Dependencies:  python >= 3.5, pyliblo

      This python script, and all of OSC_Tools is licensed
      under the GNU GPL version 3.

      OSC Whispers recieves OSC Messages and forwards the message to a new
      location(s) based on the messages Path Prefix.

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

from OSCToolkit.OSCWhispers import *


# Main Loop
if __name__ == "__main__":

    # Load and parse configuration file
    CONFIG_FILE_LOCATIONS = [
            'osctoolkit.conf', 
            '/home/$USER/.config/osctoolkit.conf', 
            '/etc/osctoolkit.conf',
            ]
    config = ConfigFile(CONFIG_FILE_LOCATIONS)

    # Parse command lie arguments
    arguments = ParseArgs(config.configData)

    # Load and parse OTW Files
    '''
        This will eventually depend on the mutually exclusive arguments of
        -f and -d as to what list is used for OTWFiles()
    '''
    otwFiles = OTWFiles(
            arguments.argData[
                'otwFileLocations'
                ])

    osc = OSC(
            config.configData['serverListenPort'],
            otwFiles.otwFileData['forwardingRules'],
            otwFiles.otwFileData['oscTargets'],
            )

    ## Main Loop
    while True:
        osc.listenServer.recv(osc.MAIN_LOOP_LATENCY)
