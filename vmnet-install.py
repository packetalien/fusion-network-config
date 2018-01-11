#!/usr/bin/env python
# ========================================================================
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
# ========================================================================
# [1] https://blog.shichao.io/2012/10/04/progress_speed_indicator_for_urlretrieve_in_python.html
# Functions reporthook and save adapted/copied from [1]
#
# This script was lightly tested and only compatible with MacOS. This
# script should be considered raw.
#
# Version 0.1


import os
import sys
import time
import getpass
import urllib
import urllib2
import hashlib
import fnmatch
from os.path import expanduser
from subprocess import call

# Script Configuration and Variables
# Todo

# List of Varabiles, not used, but left for reference and configuration reasons, do not delete.

vmnetfile = "fusion-vmnet-full.txt"
fusionconf = 'https://raw.githubusercontent.com/packetalien/fusion-network-config/master/fusion-vmnet-config.txt'

# Functions

def reporthook(count, block_size, total_size):
    global start_time
    if count == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(count * block_size)
    speed = int(progress_size / (1024 * duration))
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write("\r...%d%%, %d MB, %d KB/s, %d seconds passed" %
                    (percent, progress_size / (1024 * 1024), speed, duration))
    sys.stdout.flush()

def save(url, filename):
    urllib.urlretrieve(url, filename, reporthook)

def filecheck(filename):
    user,home = getuser()
    basedir = "/Documents/Virtual Machines.localized/IT-Managed-VMs"
    searchdir = home + basedir
    for base, dirs, files, in os.walk(searchdir):
        if filename in files:
            return True

def getuser():
    localuser = getpass.getuser()
    home = expanduser("~")
    return localuser, home

def vmnetconfig(filename):
    user,home = getuser()
    basedir = "/Documents/Virtual Machines.localized/IT-Managed-VMs/"
    vmnetworkingdir = home + basedir + vmnetfile
    fusionnetdir = '/Library/Preferences/VMware Fusion/'
    fusionnetbuild = fusionnetdir + "networking"
    call(["cp","-f",vmnetworkingdir,fusionnetbuild])

# This main file is customized for Palo Alto Networks IT. It is recommended that
# you change the basedir directories to suit your needs.

def main():
    if filecheck(vmnetfile):
        print("File already downloaded.")
        user,home = getuser()
        basedir = "/Documents/Virtual Machines.localized/IT-Managed-VMs/"
        vmnetworkingdir = home + basedir + vmnetfile
        vmnetconfig(vmnetfile)
        call(["/Applications/VMware Fusion.app/Contents/Library/vmnet-cli","--configure"])
        call(["/Applications/VMware Fusion.app/Contents/Library/vmnet-cli","--stop"])
    else:
        user,home = getuser()
        basedir = "/Documents/Virtual Machines.localized/IT-Managed-VMs/"
        vmnetworkingdir = home + basedir + vmnetfile
        save(fusionconf,vmnetfile)
        vmnetconfig(vmnetfile)
        call(["/Applications/VMware Fusion.app/Contents/Library/vmnet-cli","--configure"])
        call(["/Applications/VMware Fusion.app/Contents/Library/vmnet-cli","--stop"])



if __name__ == "__main__":
    main()
