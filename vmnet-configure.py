#!/usr/bin/env python
# Copyright (c) 2022, Palo Alto Networks
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# Author: Richard Porter rporter@paloaltonetworks.com>

'''
Palo Alto Networks |vmnet-configure.py|

This file configures VMWare Fusion Network settings.

This software is provided without support, warranty, or guarantee.
Use at your own risk.
'''
__author__ = "Richard Porter (@packetalien)"
__copyright__ = "Copyright 2022, Palo Alto Networks"
__version__ = "1.5"
__license__ = "MIT"
__status__ = "Production"


from distutils import errors
import os
import sys
import time
import getpass
import hashlib
import fnmatch
import json
import pip
import importlib
import logging
import webbrowser
import shutil
import json
import glob
import logging
from shutil import rmtree
from urllib import request
from time import strftime
from time import sleep
from platform import system
from subprocess import call
from subprocess import Popen
from logging.handlers import RotatingFileHandler
from os.path import expanduser
from os import path
from shutil import copy

'''
Setting up a simple logger. Check 'controller.log' for
logger details.
'''

logger = logging.getLogger(__name__)
logLevel = 'DEBUG'
maxSize = 10000000
numFiles = 10
handler = RotatingFileHandler(
    'controller.log', maxBytes=maxSize, backupCount=numFiles
    )
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel("DEBUG")


'''
Setting context for SSL inspection compatibility. Comment
out and remove context from urllib.urlopen().
'''

# Script Configuration and Variable

update_banner = r'''
.=====================================================.
||                                                   ||
||   _       _--""--_                                ||
||     " --""   |    |   .--.           |    ||      ||
||   " . _|     |    |  |    |          |    ||      ||
||   _    |  _--""--_|  |----| |.-  .-i |.-. ||      ||
||     " --""   |    |  |    | |   |  | |  |         ||
||   " . _|     |    |  |    | |    `-( |  | ()      ||
||   _    |  _--""--_|             |  |              ||
||     " --""                      `--'              ||
||                                                   ||
`=====================================================
You are about to change VMWare Fusion's network
settings. This is permenant and will DELETE
previous networks settings. The original network file
can be found with a .bak extension.

ARE YOU SURE YOU WISH TO PROCEED? 

Enter YES exactly to proceed!
Enter NO to exit!
'''

no_banner = r'''
Art by Shanaka Dias
            __:.__
           (_:..'"=
            ::/ o o\         AHAH!
           ;'-'   (_)     Spaceman Spiff      .
           '-._  ;-'        wins again !  _'._|\/:
           .:;  ;   .            .         '- '   /_
          :.. ; ;,   \            \       _/,    "_<
         :.|..| ;:    \            \__   '._____  _)
         :.|.'| ||   And I wanted             _/ /
         :.|..| :'     to delete things!     `;--:
         '.|..|:':       _               _ _ :|_\:
      .. _:|__| '.\.''..' ) ___________ ( )_):|_|:
:....::''::/  | : :|''| "/ /_=_=_=_=_=/ :_[__'_\3_)
 ''      '-''-'-'.__)-'
'''

# TODO: Turn this into a CONF file.
vmnetfile = "fusion-vmnet-config.txt"
url = 'https://raw.githubusercontent.com/packetalien/fusion-network-config/master/fusion-vmnet-config.txt'
funsioncfgfile = 'networking'

# Functions

'''
Attribute: verify=False is set for Decryption compatibility
for corporate use. This disables SSL Certificate Validation.
This is considered dangerous. Disable this unless you are 
100% sure of what you are doing! You've BEEN WARNED.
'''

def save(url, filename):
    '''
    Simple download function based on requests. Takes in
    a url and a filename. Saves to directory filemane indicates.
    '''
    try:
        print("Getting File.... %s" % (filename))
        sleep(2)
        request.urlretrieve(url,filename)
    except:
        print("Soemthing went wrong in save() and the program cannot continue safely.")
        print("\n\nExiting...")
        exit()

def filecheck(filename):
    '''
    Check for file.
    Returns True or False.
    '''
    for base, dirs, files, in os.walk(getuser()):
        if filename in files:
            return True

def filecheckcfg(filename):
    basedir = '/Library/Preferences/'
    searchdir = basedir
    for base, dirs, files, in os.walk(searchdir):
        if filename in files:
            return True

def vmnetconfig(filename):
    try:
        vmnetworkingdir = getuser() + os.sep + filename
        fusionnetdir = '/Library/Preferences/VMware Fusion/'
        fusionnetbuild = fusionnetdir + "networking"
        logger.debug("Executing cp function")
        call(["sudo","cp","-f",vmnetworkingdir,fusionnetbuild])
    except OSError as err:
        logger.debug(err)
        print(err)

def backupcurrentconfig(filename):
    try:
        fusionnetdir = '/Library/Preferences/VMware Fusion/'
        fusionnetbuild = fusionnetdir + "networking"
        if filecheckcfg(filename):
            fusionbak = fusionnetbuild + filetimestamp()
            logger.debug("Backed up Fusion to file: %s"% fusionbak)
            call(["sudo","cp","-f",fusionnetbuild,fusionbak])
        else:
            logger.debug(
                "Ran into an issue locating the networking config file. Is Fusion installed?"
                )
            print(
                "File does not exists, have you started/installed VMWare Fusion? \
                    Please join #labinabox on Slack for troubleshooting and support."
                )
    except OSError as err:
        logger.debug(err)
        print(err)

def filetimestamp():
    try:
        filetimestamp = time.strftime("%Y%m%d-%H%M%S")
        tagstamp = filetimestamp + ".bak"
        logger.debug("Returning %s" % tagstamp)
        return tagstamp
    except OSError as err:
        logger.debug(err)
        print(err)

def getuser():
    try:
        home = expanduser("~")
        return home
    except OSError as err:
        logger.debug(err)
        print(err)

def verify_delete():
    answer = None 
    print(update_banner)
    while answer not in ("yes", "no"): 
        answer = input("Enter yes or no: ") 
        if answer == "yes": 
            print("{:-^30s}".format("Starting Network Configuration."))
        elif answer == "no": 
             print("Installer will Exit in 10 seconds.")
             print("Log into Slack #labinabox for help.")
             sleep(5)
             print(no_banner)
             sleep(5)
             #exit() 
        else: 
        	print("Please enter yes or no.")

# This main file is customized for Palo Alto Networks IT. It is recommended that
# you change the basedir directories to suit your needs.

def main():
    print("\n")
    try:
        if filecheck(vmnetfile):
            print("File already downloaded. Continuing with process.")
            logger.debug("File already downloaded. Starting backup process.")
            backupcurrentconfig(funsioncfgfile)
            logger.debug("Current Fusion network config backed up.")
            vmnetconfig(vmnetfile)
            logger.debug(
                "New networking file loaded. Restarting network processes."
                )
            call(
                ["sudo","/Applications/VMware Fusion.app/Contents/Library/vmnet-cli","--stop"]
                )
            call(
                ["sudo","/Applications/VMware Fusion.app/Contents/Library/vmnet-cli","--configure"]
                )
            call(
                ["sudo","/Applications/VMware Fusion.app/Contents/Library/vmnet-cli","--start"]
                )
        else:
            logger.debug("Starting backup process.")
            backupcurrentconfig(funsioncfgfile)
            logger.debug("Backup complete, getting config file.")
            logger.debug("Saving file: %s" %  (getuser() + os.sep + vmnetfile))
            save(url, getuser() + os.sep + vmnetfile)
            logger.debug("Setting up new Fusion networking config")
            vmnetconfig(vmnetfile)
            logger.debug(
                "New networking file loaded. Restarting network processes."
                )
            call(
                ["sudo","/Applications/VMware Fusion.app/Contents/Library/vmnet-cli","--stop"]
                )
            call(
                ["sudo","/Applications/VMware Fusion.app/Contents/Library/vmnet-cli","--configure"]
                )
            call(
                ["sudo","/Applications/VMware Fusion.app/Contents/Library/vmnet-cli","--start"]
                )
    except OSError as err:
        logger.debug(err)
        print(err)

if __name__ == "__main__":
    main()
