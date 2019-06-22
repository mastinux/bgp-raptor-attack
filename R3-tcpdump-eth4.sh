#!/bin/bash

sudo python ./run.py --node R3 --cmd "tcpdump -nl -i R3-eth4 \"src host 11.1.0.1 and (dst host 12.2.0.1 or dst host 12.3.0.1) and tcp[tcpflags] & (tcp-ack) != 0\""

