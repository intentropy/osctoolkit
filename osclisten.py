#!/usr/bin/python3
"""
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
"""

from OSCToolkit.OSCListen   import *



MAIN_LOOP_LATENCY = 1



if __name__ == '__main__':
    # Load Configuration File
    CONFIG_FILE_LOCATIONS = [
            'osctoolkit.conf'                       , 
            '/home/$USER/.config/osctoolkit.conf'   , 
            '/etc/osctoolkit.conf'                  ,
            ]
    config = ConfigFile( CONFIG_FILE_LOCATIONS )

    # Parse Arguments
    arguments = ParseArgs( config.configData )
    
    # Setup, Build, and register each OSC server on each listen port from config and args
    listenPorts = config.configData[ 'listenPorts' ] + arguments.argData[ 'listenPorts' ]
    setupOSCServers( listenPorts )
    buildOSCServers( listenPorts )

    # Verbosely display listen ports if enabled
    if config.configData[ 'verboseListenPorts' ] or arguments.argData[ 'verboseListenPorts' ] == True:
        displayListenPorts( listenPorts )

    # Display MOTD 
    if config.configData[ 'verboseMotd' ] or arguments.argData[ 'verboseMotd' ]:
        displayMOTD(
                config.configData[ 'motd' ]
                )
    
    # Main Loop
    while exitCall == False:
        for oscServerId in oscListenServers:
            oscServerId.recv( MAIN_LOOP_LATENCY )
