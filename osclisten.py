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

from osctoolkit import osclisten


if __name__ == '__main__':

    # Load Config file
    '''
        osclisten.ConfigFile takes the potential locations of the configuration file in order in which
        to check for the file.  Once a file is found it is loaded (osclisten.ConfigFile.loadConfigFile),
        and broken into lines.  The lines are passed to osclisten.ConfigFile.parseConfigFile, and
        the values are stored in a dictionary called configData.
    '''
    CONFIG_FILE_LOCATIONS = ['osctoolkit.conf', 
            '/home/$USER/.config/osctoolkit.conf', 
            '/etc/osctoolkit.conf']
    config = osclisten.ConfigFile(CONFIG_FILE_LOCATIONS)

    # Parse Arguments
    arguments = osclisten.ParseArgs()
    
    # Setup, Build, and register each OSC server on each listen port from config and args
    listenPorts = config.configData['listenPorts'] + arguments.argData['listenPorts']
    osclisten.setupOSCServers(listenPorts)
    osclisten.buildOSCServers(listenPorts)

    # Verbosely display listen ports if enabled
    if config.configData['verboseListenPorts'] or arguments.argData['verboseListenPorts'] == True:
        osclisten.displayListenPorts(listenPorts)
        # Display MOTD 
        osclisten.displayMOTD()
    
    # Main Loop
    MAIN_LOOP_LATENCY = 1
    while osclisten.exitCall == False:
        for oscServerId in osclisten.oscListenServers:
            oscServerId.recv(MAIN_LOOP_LATENCY)
