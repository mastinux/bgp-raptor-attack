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
	os.system('pgrep torrc | xargs kill -9')
	os.system('pgrep zebra | xargs kill -9')
	os.system('pgrep bgpd | xargs kill -9')
	os.system('pgrep -f torrc | xargs kill -9')
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

		if router.name == "R1":
			router.cmd("tcpdump -i R1-eth4 -w /tmp/R1-eth4.pcap not arp > /tmp/tcpdump-R2-eth4.out 2> /tmp/tcpdump-R2-eth4.err &", shell=True)
			router.cmd("tcpdump -i R1-eth5 -w /tmp/R1-eth5.pcap not arp > /tmp/tcpdump-R2-eth5.out 2> /tmp/tcpdump-R2-eth5.err &", shell=True)

	log2("sysctl changes to take effect", args.sleep, "cyan")

	for router in net.switches:
		router.cmd("~/quagga-1.2.4/zebra/zebra -f conf/zebra-%s.conf -d -i /tmp/zebra-%s.pid > logs/%s-zebra-stdout 2>&1" % (router.name, router.name, router.name))
		router.waitOutput()

		router.cmd("~/quagga-1.2.4/bgpd/bgpd -f conf/bgpd-%s.conf -d -i /tmp/bgp-%s.pid > logs/%s-bgpd-stdout 2>&1" % (router.name, router.name, router.name), shell=True)
		router.waitOutput()

		log("Starting zebra and bgpd on %s" % router.name)
	
	# configuring IP and default gateway on hosts
	for host in net.hosts:
		host.cmd("ifconfig %s-eth0 %s" % (host.name, getIP(host.name)))
		host.cmd("route add default gw %s" % (getGateway(host.name)))

	# starting web servers
	for i in xrange(NUM_ASES):
		log("Starting web servers", 'yellow')
		startWebserver(net, 'h%s-1' % (i+1), "Web server home page")

	log2("BGP convergence", 10, "cyan")
	
	# setting ownership
	os.system("chown -R root:root chutney/net/nodes/")

	# configuring tor on hosts
	hostname = "h5-3"
	host = net.getNodeByName(hostname)
	host.popen("tor/src/app/tor -f chutney/net/nodes/000authority/torrc > /tmp/tor-%s.log 2>&1 &" % hostname, shell=True)

	hostname = "h2-2"
	host = net.getNodeByName(hostname)
	host.popen("tor/src/app/tor -f chutney/net/nodes/001authority/torrc > /tmp/tor-%s.log 2>&1 &" % hostname, shell=True)

	hostname = "h6-2"
	host = net.getNodeByName(hostname)
	host.popen("tor/src/app/tor -f chutney/net/nodes/002exit/torrc > /tmp/tor-%s.log 2>&1 &" % hostname, shell=True)

	hostname = "h1-1"
	host = net.getNodeByName(hostname)
	host.popen("tor/src/app/tor -f chutney/net/nodes/003client/torrc > /tmp/tor-%s.log 2>&1 &" % hostname, shell=True)

	log2("Tor topology convergence", 60, "cyan")

	hostname = "h4-1"
	host = net.getNodeByName(hostname)
	host.popen("ifconfig > ~/merda.log 2>&1", shell=True)
	host.popen("netstat -lnp >> ~/merda.log 2>&1", shell=True)

	hostname = "h1-1"
	host = net.getNodeByName(hostname)
	host.popen("wget -o ~/merdaccia -O ~/merdaccia.html 14.1.0.1", shell=True)
	host.popen("torsocks wget -o ~/merdone -O ~/merdone.html 14.1.0.1", shell=True)
	log2("h1-1 to perform torsocks wget against h4-1", 5, "cyan")

	#CLI(net)
	#net.stop()

	os.system('pgrep zebra | xargs kill -9')
	os.system('pgrep bgpd | xargs kill -9')
	os.system('pgrep -f torrc | xargs kill -9')
	os.system('pgrep -f webserver.py | xargs kill -9')

	# resetting ownership
	os.system("chown -R mininet:mininet chutney/net/nodes/")

    # opening capture files
	fltr = '(ip.addr == 11.1.0.1) or (ip.addr == 12.2.0.1) or (ip.addr == 14.1.0.1) or (ip.addr == 15.3.0.1) or (ip.addr == 16.2.0.1)'
	#os.system('sudo wireshark /tmp/R1-eth4.pcap -Y \'%s\' &' % fltr)
	#os.system('sudo wireshark /tmp/R1-eth5.pcap -Y \'%s\' &' % fltr)
	os.system("gedit ~/merda.log ~/merdone ~/merdone.html ~/merdaccia ~/merdaccia.html")


if __name__ == "__main__":
	main()
