#! /usr/bin/python

#Hello fellow hackers! My name is Defalt.
#This is a re-write of an older tool that I made
#You can see the old version here: http://pastebin.com/EyF6xGkw
#Happy Hacking! -Defalt

import sys
try:
	from logging import getLogger, ERROR
	getLogger('scapy.runtime').setLevel(ERROR)
	from scapy.all import *
	conf.verb = 0
except ImportError:
	print '[!] Failed to Import Scapy'
	sys.exit(1)

class ArpEnumerator(object):
	def __init__(self, interface=False, passive=False, range=False, output=False):
		self.interface = interface
		self.passive = passive
		self.range = range
		self.output = output
		self.discovered_hosts = {}
		self.filter = 'arp'
	def passive_handler(self, pkt):
		try:
			if not pkt[ARP].psrc in self.discovered_hosts.keys():
				print "%s - %s" %(pkt[ARP].psrc, pkt[ARP].hwsrc)
				self.discovered_hosts[pkt[ARP].psrc] = pkt[ARP].hwsrc
		except Exception:
			return
		except KeyboardInterrupt:
			return
	def passive_sniffer(self):
		if not self.range:
			print '[*] No Range Given; Sniffing All ARP Traffic'
		else:
			self.filter += ' and (net %s)' %(self.range)
		print '[*] Sniffing Started on %s\n' %(self.interface)
		try:
			sniff(filter=self.filter, prn=self.passive_handler, store=0)
		except Exception:
			print '\n[!] An Unknown Error Occured'
			return
		print '\n[*] Sniffing Stopped'
	def active_scan(self):
		print '[*] Scanning for Hosts... ',
		sys.stdout.flush()
		try:
			ans = srp(Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(pdst=self.range), timeout=2, iface=self.interface, inter=0.1)[0]
		except Exception:
			print '[FAIL]'
			print '[!] An Unknown Error Occured'
			return
		print '[DONE]\n[*] Displaying Discovered Hosts:\n'
		for snd, rcv in ans:
			self.discovered_hosts[rcv[ARP].psrc] = rcv[ARP].hwsrc
			print '%s - %s' %(rcv[ARP].psrc, rcv[ARP].hwsrc)
		print '\n[*] Scan Complete'
		return
	def output_results(self):
		print '[*] Writing to Output File...',
		try:
			with open(self.output, 'w') as file:
				for key, val in self.discovered_hosts.items():
					file.write('%s - %s\n' %(key, val))
			print '[DONE]\n[*] Successfully Wrote to Output File'
			return
		except IOError:
			print '\n[!] Failed to Write Output File'
			return

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='ARP-based Network Enumeration Tool')
	parser.add_argument('-i', '--interface', help='Network interface to scan/sniff on', action='store', dest='interface', default=False)
	parser.add_argument('-r', '--range', help='Range of IPs in CIDR notation', action='store', dest='range', default=False)
	parser.add_argument('--passive', help='Enable passive mode (No packets sent, sniff only)', action='store_true', dest='passive', default=False)
	parser.add_argument('-o', '--output', help='Output scan results to text file', action='store', dest='file', default=False)
	args = parser.parse_args()
	if not args.interface:
		parser.error('No network interface given')
	elif (not args.passive) and (not args.range):
		parser.error('No range specified for active scan')
	else:
		pass
	if args.passive:
		if not not args.range:
			if not not args.file:
				enum = ArpEnumerator(interface=args.interface, passive=True, range=args.range, output=args.file)
				enum.passive_sniffer()
				enum.output_results()
				sys.exit(0)
			else:
				enum = ArpEnumerator(interface=args.interface, passive=True, range=args.range)
				enum.passive_sniffer()
				sys.exit(0)
		else:
			if not not args.file:
				enum = ArpEnumerator(interface=args.interface, passive=True, output=args.file)
				enum.passive_sniffer()
				enum.output_results()
				sys.exit(0)
			else:
				enum = ArpEnumerator(interface=args.interface, passive=True)
				enum.passive_sniffer()
				sys.exit(0)
	else:
		if not not args.file:
			enum = ArpEnumerator(interface=args.interface, range=args.range, output=args.file)
			enum.active_scan()
			enum.output_results()
			sys.exit(0)
		else:
			enum = ArpEnumerator(interface=args.interface, range=args.range)
			enum.active_scan()
			sys.exit(0)
