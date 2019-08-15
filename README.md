# fusion-network-config

VMWare Fusion Networking Config Baseline

# Description

This file is to configure VMWare Fusion Networking to insure IP compatibility for Virtual Machine Sharing. It is intended for Palo Alto Networks Systems Engineers, however, open to anyone. The goal is to insure that networking within the local virtual enviroment matches for lab exchange compatibility.

# Use

*This script will need sudo or root to make system changes, use with caution. This script edits vmnet settings for VMware Fusion on MacOS.*

* vmnet1 - 192.168.45.0/24
* vmnet2 - 192.168.35.0/24
* vmnet3 - 192.168.25.0/24
* vmnet4 - 192.168.15.0/24
* vmnet5 - 192.168.5.0/24
* vmnet8 - 192.168.55.0/24

sudo python ./vmnet-install-full-pull.py

# Author

Richard Porter, packetalien@packetalien.com, @packetalien - twitter packetalien - keybase
