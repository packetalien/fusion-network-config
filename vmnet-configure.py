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

'''
Palo Alto Networks |vmnet-configure.py|

This file configures VMWare Fusion Network settings.

This software is provided without support, warranty, or guarantee.
Use at your own risk.
'''
__author__ = "Richard Porter (@packetalien)"
__copyright__ = "Copyright 2019, Palo Alto Networks"
__version__ = "1.4"
__license__ = "MIT"
__status__ = "Production"


import os
import sys
import time
import getpass
import hashlib
import fnmatch
import requests
import logging
from subprocess import call
from logging.handlers import RotatingFileHandler

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
    a url and a filename. Saves to directory that script
    is executed in.
    '''
    with open(filename, "wb") as f:
        print("Downloading %s" % filename)
        logger.debug("Downloading %s" % filename) 
        response = requests.get(url, stream=True, verify=False)
        total_length = response.headers.get('content-length')
        if total_length is None: # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write("\r[%s%s]" % ('*' * done, ' ' * (50-done)) )    
                sys.stdout.flush()

# TODO: Implement resource check and error handling
def web_resource_check(url):
    ''' Uniform Resource Locater (URL) state checker.
    This function will ask a web server if it is alive,
    expecting a 200 response in return. If a 200 response
    recieved from URL function returns a True.

    url: The function expects a web URL
    There is no error checking in the variable pass in this function yet.
    TODO: Add URL validation for the url variable.
    '''
    r = requests.get(url, verify=False)
    response = r.status_code
    logger.debug(
        "Web resource check returned a status code of: %s" % response
        )
    return response

def filecheck(filename):
    basedir = "./"
    searchdir = basedir
    for base, dirs, files, in os.walk(searchdir):
        if filename in files:
            return True

def filecheckcfg(filename):
    basedir = '/Library/Preferences/'
    searchdir = basedir
    for base, dirs, files, in os.walk(searchdir):
        if filename in files:
            return True

def vmnetconfig(filename):
    vmnetworkingdir = "./" + filename
    fusionnetdir = '/Library/Preferences/VMware Fusion/'
    fusionnetbuild = fusionnetdir + "networking"
    logger.debug("Executing cp function")
    call(["cp","-f",vmnetworkingdir,fusionnetbuild])

def backupcurrentconfig(filename):
    fusionnetdir = '/Library/Preferences/VMware Fusion/'
    fusionnetbuild = fusionnetdir + "networking"
    if filecheckcfg(filename):
        fusionbak = fusionnetbuild + filetimestamp()
        logger.debug("Backed up Fusion to file: %s"% fusionbak)
        call(["cp","-f",fusionnetbuild,fusionbak])
    else:
        logger.debug(
            "Ran into an issue locating the networking config file. Is Fusion installed?"
            )
        print(
            "File does not exists, have you started/installed VMWare Fusion? \
                Please join #labinabox on Slack for troubleshooting and support."
                )

def filetimestamp():
    filetimestamp = time.strftime("%Y%m%d-%H%M%S")
    tagstamp = filetimestamp + ".bak"
    logger.debug("Returning %s" % tagstamp)
    return tagstamp

# This main file is customized for Palo Alto Networks IT. It is recommended that
# you change the basedir directories to suit your needs.

def main():
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
            ["/Applications/VMware Fusion.app/Contents/Library/vmnet-cli","--stop"]
            )
        call(
            ["/Applications/VMware Fusion.app/Contents/Library/vmnet-cli","--configure"]
            )
        call(
            ["/Applications/VMware Fusion.app/Contents/Library/vmnet-cli","--start"]
            )
    else:
        logger.debug("Starting backup process.")
        backupcurrentconfig(funsioncfgfile)
        logger.debug("Backup complete, getting config file.")
        vmnetworkingdir = "./"
        savefile = vmnetworkingdir + vmnetfile
        logger.debug("Saving file: %s" % savefile)
        save(url,savefile)
        logger.debug("Setting up new Fusion networking config")
        vmnetconfig(vmnetfile)
        logger.debug(
            "New networking file loaded. Restarting network processes."
            )
        call(
            ["/Applications/VMware Fusion.app/Contents/Library/vmnet-cli","--stop"]
            )
        call(
            ["/Applications/VMware Fusion.app/Contents/Library/vmnet-cli","--configure"]
            )
        call(
            ["/Applications/VMware Fusion.app/Contents/Library/vmnet-cli","--start"]
            )



if __name__ == "__main__":
    main()
