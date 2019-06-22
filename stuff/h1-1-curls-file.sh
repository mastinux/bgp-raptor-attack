#!/bin/bash

# simple curl
sudo python ./run.py --node h1-1 \
	--cmd "wget 14.1.0.1/file.txt -q client/file-\"`date +%R:%S.%N`\".txt"

# curl over torsocks
#sudo python ./run.py --node h1-1 \
#	--cmd "sudo bash -c 'echo TORSOCKS_CONF_FILE=\"/home/mininet/*routing-attacks/bgp-raptor-attack/chutney/net/nodes/003client/torsocks.conf\" >> /etc/environment'"

#sudo python ./run.py --node h1-1 --cmd "sudo bash -c 'source /etc/environment'; sudo torsocks wget localhost/file.txt -qO client/file-\"`date +%R:%S.%N`\"-over-torsocks.txt"

sudo python ./run.py --node h1-1 \
	--cmd "sudo bash -c 'source script.sh'"

#sudo python ./run.py --node h1-1 --cmd "sudo bash -c 'echo TORSOCKS_CONF_FILE=\"/home/mininet/*routing-attacks/bgp-raptor-attack/chutney/net/nodes/003client/torsocks.conf\" >> /env/environment; sudo source /etc/envirnoment; sudo torsocks wget 14.1.0.1/file.txt -qO client/file-\"`date +%R:%S.%N`\"-over-torsocks.txt"
