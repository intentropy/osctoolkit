#!/usr/bin/env python
"""
OSC Midi Client
    oscmidi-client.py

      Written By: Shane Hutter

      Required Dependencies:  python >= 3.5, pyliblo, python-mido, python-rtmidi

      This python script, and all of osctoolkit is licensed
      under the GNU GPL version 3

      OSC Midi Client listens for midi events on virtual midi ports and directly
      from midi devices, and translates them into Open Sound Control messages.

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

from OSCToolkit.OSCMidiClient import *

if __name__ == "__main__":

    ## Load configuration file
    CONFIG_FILE_LOCATIONS = ['osctoolkit.conf', 
            '/home/$USER/.config/osctoolkit.conf', 
            '/etc/osctoolkit.conf']
    config = ConfigFile(CONFIG_FILE_LOCATIONS)

    ## Debug print config and arg data
    # Consider building funtions of this and others into a debug module
    for data in config.configData:
        print(data + " " + str(config.configData[data]))

