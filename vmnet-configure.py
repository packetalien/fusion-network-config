#!/usr/bin/env python
# Copyright (c) 2019, Palo Alto Networks
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
#TODO Document Functions
'''
Palo Alto Networks |fusionNet.py|

This file configures VMWare Fusion Network settings.

This software is provided without support, warranty, or guarantee.
Use at your own risk.
'''
__author__ = "Richard Porter (@packetalien)"
__copyright__ = "Copyright 2022, Palo Alto Networks"
__version__ = "1.6"
__license__ = "MIT"
__status__ = "Production"

import os
import shutil
from sqlite3 import OperationalError
import sys
import time
import getpass
import hashlib
import fnmatch
import logging
import json
import ssl
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
from urllib.error import HTTPError

logger = logging.getLogger(__name__)
logLevel = 'DEBUG'
maxSize = 10000000
numFiles = 10
handler = RotatingFileHandler(
    'fusionNet.log', maxBytes=maxSize, backupCount=numFiles
    )
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel("DEBUG")

netCFG = "https://raw.githubusercontent.com/packetalien/fusion-network-config/master/netcfg.json"
netfile = "/Library/Preferences/VMware Fusion/networking"
netfileheader = "VERSION=1,0"

# TODO: Fix this after SE Summit
ssl._create_default_https_context = ssl._create_unverified_context

def getuser():
    try:
        home = expanduser("~")
        return home 
    except OSError as err:
        print(err)
        logger.debug(err)

def filetimestamp():
    try:
        filetimestamp = time.strftime("%Y%m%d-%H%M%S")
        tagstamp = filetimestamp + ".bak"
        logger.info("Returning %s" % tagstamp)
        return tagstamp
    except OSError as err:
        print(err)
        logger.debug(err)

def getnet(netCFG):
    try:
        webURL = request.urlopen(netCFG)
        netdata = webURL.read()
        encoding = webURL.info().get_content_charset('utf-8')
        netjson = json.loads(netdata.decode(encoding))
        logger.info(netjson)
        return netjson
    except HTTPError as err:
        logger.debug(err)
        print(err)

def netmove(netfile):
    try:
        print("{:-^40s}".format("Backing up Config"))
        netfilebak = netfile + filetimestamp()
        logger.info("Moving %s" % (netfilebak))
        call(
            ["sudo", "mv" ,"-f" , netfile,
            netfilebak]
            )
        print("Moved %s to %s" % (netfile, netfilebak))
        logger.info("Moved %s to %s" % (netfile, netfilebak))
    except OSError as err:
        print(err)
        logger.debug(err)

def netcreate(newfile, netfile):
    # Function Variables
    try:
        if os.path.exists(getuser() + os.sep + "networking"):
            print("{:-^40s}".format("Moving new Config"))
            call(
                ["sudo", "mv" ,"-f" , newfile, netfile]
                )
            print("Moved %s to %s" % (newfile, netfile))
            logger.info("Moved %s to %s" % (newfile, netfile))
        else:
            print("{:-^40s}".format("ERROR"))
            print("Could Not Find File")
            print("Script will Exit. It cannot continue")
            print("{:-^40s}".format("ERROR"))
            exit()
    except OSError as err:
        print(err)
        logger.debug(err)

def netcheck(home):
    # Check for old network files
    try:
        if os.path.exists(getuser() + os.sep + "networking"):
            print("{:-^40s}".format("WARNING"))
            print("Found a networking file in %s" % (getuser()))
            print("Removing for a clean build")
            logger.info("{:-^40s}".format("WARNING"))
            logger.info("Found a networking file in %s" % (getuser()))
            logger.info("Removing for a clean build")
            os.remove(home + os.sep + "networking")
            print("{:-^40s}".format("COMPLETE"))
    except OSError as err:
        print(err)
        logger.debug(err)

def enablep():
    #Enables promiscuious mode in VMWare Fusion
    try:
        print("{:-^40s}".format("Enabling Promiscuious Mode"))
        call(
            ["sudo", "touch", "/Library/Preferences/VMware Fusion/promiscAuthorized"]
            )
    except OSError as err:
        print(err)
        logger.debug(err)

def netbuilder(netinfo, netfileheader, home):
    # network file found in:
    # /Library/Preferences/VMWare\ Fusion/networking
    #baseline answers for VMWare Fusion network file.
    vnet_prefix = "VNET_"
    dhcp_suffix = "_DHCP"
    netmask_suffix = "_HOSTONLY_NETMASK"
    subnet_suffix = "_HOSTONLY_SUBNET"
    adapter_suffix = "_VIRTUAL_ADAPTER"
    nat_suffix = "_NAT"
    logger.debug("Ran netcheck()")
    os.chdir(home)
    try:
        networking = open("networking", "a+")
        print("{:-^40s}".format("Building Network from JSON config"))
        logger.info("{:-^40s}".format("Building Network from JSON config"))
        networking.write(netfileheader + "\n")
        print(netfileheader)
        try:
            for each in netinfo:
                networking.write("answer " + vnet_prefix + netinfo.get(each).get('VNET') + dhcp_suffix + " " + netinfo.get(each).get("DHCP") + "\n")
                print("answer " + vnet_prefix + netinfo.get(each).get('VNET') + dhcp_suffix + " " + netinfo.get(each).get("DHCP"))
                networking.write("answer " + vnet_prefix + netinfo.get(each).get('VNET') + netmask_suffix + " " + netinfo.get(each).get("NETMASK") + "\n")
                print("answer " + vnet_prefix + netinfo.get(each).get('VNET') + netmask_suffix + " " + netinfo.get(each).get("NETMASK"))
                networking.write("answer " + vnet_prefix + netinfo.get(each).get('VNET') + subnet_suffix + " " + netinfo.get(each).get("SUBNET") + "\n")
                print("answer " + vnet_prefix + netinfo.get(each).get('VNET') + subnet_suffix + " " + netinfo.get(each).get("SUBNET"))
                networking.write("answer " + vnet_prefix + netinfo.get(each).get('VNET') + adapter_suffix + " " + netinfo.get(each).get("VIRTUAL_ADAPTER") + "\n")
                print("answer " + vnet_prefix + netinfo.get(each).get('VNET') + adapter_suffix + " " + netinfo.get(each).get("VIRTUAL_ADAPTER"))
                if netinfo.get(each).get("NAT") == "yes":
                    networking.write("answer " + vnet_prefix + netinfo.get(each).get('VNET') + nat_suffix + " " + netinfo.get(each).get("NAT") + "\n")
                    print("answer " + vnet_prefix + netinfo.get(each).get('VNET') + nat_suffix + " " + netinfo.get(each).get("NAT"))
        except OSError as err:
            print(err)
            logger.debug(err)
        print("{:-^40s}".format("Build Complete"))
        networking.close()
    except OSError as err:
        print(err)
        logger.debug(err)

def netstop():
    # Stop VMWare Fusion Networking
    try:
        print("{:-^40s}".format("Stopping"))
        call(
            ["sudo", "/Applications/VMware Fusion.app/Contents/Library/vmnet-cli", "--stop"]
            )
        print("{:-^40s}".format("Stopped"))
    except OSError as err:
        print(err)
        logger.debug(err)

def netstart():
    # Stop VMWare Fusion Networking
    try:
        print("{:-^40s}".format("Starting"))
        call(
            ["sudo", "/Applications/VMware Fusion.app/Contents/Library/vmnet-cli", "--start"]
            )
        print("{:-^40s}".format("Started"))
    except OSError as err:
        print(err)
        logger.debug(err)

def netconfigure():
    # Configure VMWare Fusion Networking
    try:
        print("{:-^40s}".format("vnet-cli configurator"))
        call(
            ["sudo", "/Applications/VMware Fusion.app/Contents/Library/vmnet-cli", "--configure"]
            )
        print("{:-^40s}".format("configuration complete"))
    except OSError as err:
        print(err)
        logger.debug(err)

def stop_fusion():
    '''
    Function uses osascript to stop Fusion.
    '''
    try:
        call(['osascript', '-e', 'tell application "VMWare Fusion" to quit'])
        logger.info("Stopped VMWare Fusion")
    except:
        logger.debug("Exception occured in start_fusion()")

def start_fusion():
    '''
    Function uses osascript to activate Fusion.
    '''
    try:
        call(['osascript', '-e', 'tell application "VMWare Fusion" to activate'])
        logger.info("Started VMWare Fusion")
    except:
        logger.debug("Exception occured in start_fusion()")

def main():
    try:
        netinfo = getnet(netCFG)
        home = getuser()
    except OSError as err:
        print(err)
        logger.debug(err)
    try:
        if system() == "Darwin":
            stop_fusion()
            enablep()
            netcheck(home)
            netmove(netfile)
            netbuilder(netinfo, netfileheader, home)
            netcreate(home + os.sep + "networking", netfile)
            start_fusion()
            netstop()
            netconfigure()
            netstart()
            #shutil.rmtree(home + os.sep + "networking")
        else:
            logger.debug("Not MacOS, found %s" % system())
            print("Not MacOS, found %s" % system())
    except OSError as err:
        logger.debug(err)
        print(err)

if __name__ == "__main__":
    main()
