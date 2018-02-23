#!/usr/bin/env python3
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
#from osctoolkit import OSCShout
from OSCToolkit.OSCShout import *

if __name__ == "__main__":
    # Parse comand line arguments
    arguments = ParseArgs()

    # Create an OSC Client and send a message based on command line arguments
    sendOSC(
            createOSCClient(
                arguments.argData['oscTargetIp'], 
                arguments.argData['oscTargetPort']), 
            arguments.argData['oscTargetPath'], 
            arguments.argData['oscArgList'],
            )
