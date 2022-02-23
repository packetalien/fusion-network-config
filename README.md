# Description

This file is to configure VMWare Fusion Networking to insure IP compatibility for Virtual Machine Sharing. It is intended for Palo Alto Networks Systems Engineers, however, open to anyone. The goal is to insure that networking within the local virtual enviroment matches for lab exchange compatibility.

# Use

curl -o $HOME/vmnet-configure.py https://raw.githubusercontent.com/packetalien/fusion-network-config/master/vmnet-configure.py

python3 $HOME/vmnet-configure.py

This script creates:

* vmnet1 - 192.168.45.0/24
* vmnet2 - 192.168.35.0/24
* vmnet3 - 192.168.25.0/24
* vmnet4 - 192.168.15.0/24
* vmnet5 - 192.168.5.0/24
* vmnet8 - 192.168.55.0/24

# Author

Richard Porter, packetalien@packetalien.com 

