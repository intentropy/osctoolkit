#!/usr/bin/env python3
"""
OSC Midi Server
    OSCMidiServer.py

    Written by: Shane Hutter

    Required Dependencies:  python >= 3.5, pyliblo, mido, rtmidi

      The OSC Midi Server module contains all the functions and classes required
      to run OSC Midi Server.

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
from argparse import ArgumentParser
from liblo import Server, ServerError
from mido import open_input, open_output, Parser
from sys import exit
from os.path import isfile
