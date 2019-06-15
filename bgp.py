#!/usr/bin/env python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import lg, info, setLogLevel
from mininet.util import dumpNodeConnections, quietRun, moveIntf
from mininet.cli import CLI
from mininet.node import Switch, OVSKernelSwitch

from subprocess import Popen, PIPE, check_output
from time import sleep, time
from multiprocessing import Process
from argparse import ArgumentParser

import sys
import os
import termcolor as T
import time

NUM_ASES = 6
NUM_HOSTS_PER_ASES = 3

from utils import *

setLogLevel('info')

parser = ArgumentParser("Configure simple BGP network in Mininet.")
parser.add_argument('--rogue', action="store_true", default=False)
parser.add_argument('--sleep', default=3, type=int)
args = parser.parse_args()

FLAGS_rogue_as = args.rogue
ROGUE_AS_NAME = 'R4'

QUAGGA_STATE_DIR = '/var/run/quagga-1.2.4'

def log(s, col="green"):
	print T.colored(s, col)


class Router(Switch):

	ID = 0

	def __init__(self, name, **kwargs):
		kwargs['inNamespace'] = True
		Switch.__init__(self, name, **kwargs)
		Router.ID += 1
		self.switch_id = Router.ID

	@staticmethod
	def setup():
		return

	def start(self, controllers):
		pass

	def stop(self):
		self.deleteIntfs()

	def log(self, s, col="magenta"):
		print T.colored(s, col)


class SimpleTopo(Topo):

	def __init__(self):
		# Add default members to class.
		super(SimpleTopo, self ).__init__()
		"""
		num_hosts_per_as = 3
		num_ases = 3
		num_hosts = num_hosts_per_as * num_ases
		"""

		# The topology has one router per AS
		routers = []
		for i in xrange(NUM_ASES):
			router = self.addSwitch('R%d' % (i+1))
			routers.append(router)

		hosts = []
		for i in xrange(NUM_ASES):
			router = 'R%d' % (i+1)

			for j in xrange(NUM_HOSTS_PER_ASES):
				hostname = 'h%d-%d' % (i+1, j+1)
				host = self.addNode(hostname)
				hosts.append(host)
				self.addLink(router, host)

		# adding links between ASes
		self.addLink('R1', 'R2')
		self.addLink('R1', 'R5')
		self.addLink('R2', 'R3')
		self.addLink('R2', 'R5')
		self.addLink('R3', 'R4')
		self.addLink('R3', 'R5')
		self.addLink('R4', 'R5')
		self.addLink('R4', 'R6')
		self.addLink('R5', 'R6')

		return


def getIP(hostname):
	AS, idx = hostname.replace('h', '').split('-')

	AS = int(AS)

	ip = '%s.%s.0.1/24' % (10+AS, idx)

	return ip


def getGateway(hostname):
	AS, idx = hostname.replace('h', '').split('-')

	AS = int(AS)

	gw = '%s.%s.0.254' % (10+AS, idx)

	return gw


def startWebserver(net, hostname, text="Default web server"):
	host = net.getNodeByName(hostname)

	return host.popen("python webserver.py --text '%s' > /tmp/%s.log" % (text, hostname), shell=True)


def init_quagga_state_dir():
	if not os.path.exists(QUAGGA_STATE_DIR):
		os.makedirs(QUAGGA_STATE_DIR)

	os.system('chown mininet:mininet %s' % QUAGGA_STATE_DIR)

	return


def main():
	os.system("rm -f /tmp/R*.log /tmp/h*.log /tmp/*R*.pid logs/*stdout")
	os.system("mn -c >/dev/null 2>&1")
	os.system("killall -9 zebra bgpd > /dev/null 2>&1")
	os.system('pgrep -f webserver.py | xargs kill -9')
	os.system('reset')

	init_quagga_state_dir()

	net = Mininet(topo=SimpleTopo(), switch=Router)
	net.start()

	# configuring routers
	for router in net.switches:
		# 0 = no RPF
		# 1 = RPF strict mode
		# 2 = RPF loose mode
		router.cmd("sysctl -w net.ipv4.conf.all.rp_filter=2")

		router.cmd("sysctl -w net.ipv4.ip_forward=1")
		router.waitOutput()

	log2("sysctl changes to take effect", args.sleep, "cyan")

	for router in net.switches:
		router.cmd("~/quagga-1.2.4/zebra/zebra -f conf/zebra-%s.conf -d -i /tmp/zebra-%s.pid > logs/%s-zebra-stdout 2>&1" % (router.name, router.name, router.name))
		router.waitOutput()

		router.cmd("~/quagga-1.2.4/bgpd/bgpd -f conf/bgpd-%s.conf -d -i /tmp/bgp-%s.pid > logs/%s-bgpd-stdout 2>&1" % (router.name, router.name, router.name), shell=True)
		router.waitOutput()

		log("Starting zebra and bgpd on %s" % router.name)
	
	# configuring hosts
	for host in net.hosts:
		host.cmd("ifconfig %s-eth0 %s" % (host.name, getIP(host.name)))
		host.cmd("route add default gw %s" % (getGateway(host.name)))

	for i in xrange(NUM_ASES):
		log("Starting web servers", 'yellow')
		startWebserver(net, 'h%s-1' % (i+1), "Web server home page")

	CLI(net)
	net.stop()

	os.system('pgrep zebra | xargs kill -9')
	os.system('pgrep bgpd | xargs kill -9')
	os.system('pgrep -f webserver.py | xargs kill -9')

if __name__ == "__main__":
	main()
