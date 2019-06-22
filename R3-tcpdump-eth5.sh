#!/bin/bash

sudo python ./run.py --node R3 --cmd "tcpdump -ln -i R3-eth5 \"src host 16.2.0.1 and dst host 14.1.0.1 and tcp[tcpflags] & (tcp-ack) != 0\""

