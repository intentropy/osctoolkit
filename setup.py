#!/usr/bin/env python
"""
    Setup script for installing OSC Toolkit
"""

from distutils.core import setup

setup(
        name                = 'osctoolkit'                          ,
        version             = '0.0.2'                               ,
        author              = 'Shane Hutter'                        ,
        author_email        = 'shane@intentropycs.com'              ,
        description         = 'Python wrapper module for xdotool'   ,
        long_description    = open( 'README.md' ).read()            ,
        license             = open( 'LICENSE' ).read()              ,
        packages            = [ 'OSCToolkit' , ]                    ,
        data_files          = [
            ( '/usr/bin'                ,   # Executable Scripts
                [
                    'osclisten'     ,
                    'oscshout'      ,
                    'oscwhispers'   ,
                    ]                                   ,
                )   ,   
            ( '/etc'                    ,   # Configuration files
                [ 'osctoolkit.conf' , ]                 ,
                )   ,
            ( '/usr/share/osctoolkit'   ,   # User resources
                [ 'example.otw' , ]                     ,
                )   ,
            ( '/usr/lib/systemd/user'   ,   # Systemd units/timers
                [ 'systemd/oscwhispersd.service' , ]    ,
                )   ,   
            ]                                                       ,

        )

