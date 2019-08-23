#!/usr/bin/python
import pexpect
import sys
import re

# Script for looking for interfaces descriptions specified with some options
# or undescripted interfaces and then set interface description "Unused"

USER = 'admin'
cisco_routers = open('cisco.txt')

# function for find interface with some match options, or undescription
# we take a one argument - list with strings of interface description command
# without header information, for example
# ['Fa0/0		up 		up 		internet', 'Fa1/0	down		down	LAN_NETWORK']
def get_free_int(lst):
	desc_base = {}
	for line in lst:
	
		# By default cisco show 4 rows with data by command
		# show interfaces description
		# Interface Status Protocol Description
		# but if interface has no description, when splitting
		# we'll get 3 rows on such interfaces
		
		if len(line.split()) == 4:
		
		# first we looking for strings with 4 rows
		# and matching them with some default descrtiptions 
		# that could configured by some engineers
			
			if re.findall('[Ff]ree', line.split()[3]):
			
			    # such interfaces we put into dict with interface name
				# and set the value 'Unused' 
				
				desc_base[line.split()[0]] = 'Unused'
				
		elif len(line.split()) < 4:
		
			# if interface have no description(length of the split string < 4)
			# put into dict key - interface name value - 'Unused'
			
			desc_base[line.split()[0]] = 'Unused'
			
	# return dict for subsequent configuration change
	
	return desc_base
	

for IP in cisco_routers.read().strip().split():
	print ('Connecting to {} ...'.format(IP))
	with pexpect.spawn('ssh {}@{}'.format(USER, IP)) as ssh:
		
		ssh.expect('[Pp]assword:')
		ssh.sendline('Juniper')
		
		ssh.expect('#')
		
		# send command for get interface description data
		ssh.sendline('sh int desc')
		
		ssh.expect('#')
		
		# splitting string with \n to list
		intf_desc = ssh.before.split('\n')[2:-1]
		
		
		print (get_free_int(intf_desc))
		

		print
		
		
		if len(get_free_int(intf_desc)) > 0:
			#print ('go working')
			ssh.sendline('configure terminal')
			ssh.expect('#')
			for interface in get_free_int(intf_desc).keys():
				ssh.sendline('interface {}'.format(interface))
				ssh.expect('#')
				
				ssh.sendline('description {}'.format(get_free_int(intf_desc)[interface]))
				ssh.expect('#')
				
		ssh.sendline('end')
		ssh.expect('#')
				
		ssh.sendline('write')
		ssh.expect('#')
				#print interface, get_free_int(intf_desc)[interface]


