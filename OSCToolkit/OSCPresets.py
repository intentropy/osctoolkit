#!/usr/bin/env python3
"""
OSC Presets
    OSCPresets.py

    Written by: Shane Hutter

    Required Dependencies:  python >= 3.5, pyliblo, mido, rtmidi

      The OSC Presets module contains all of the functions and classes
      required to run OSC Presets

      OSC Presets is a part of osctoolkit

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
