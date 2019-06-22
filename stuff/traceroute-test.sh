#!/bin/bash

reset

sudo python ./run.py --snode h1-1 --dnode h2-1 --cmd "traceroute -n"

sudo python ./run.py --snode h6-1 --dnode h4-1 --cmd "traceroute -n"

