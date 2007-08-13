# coding: latin-1

from __future__ import with_statement
from commands import Command
import re
from socket import *

from socket import * 
from struct import * 
 
def tw_get_num_players(address, port): 
    sock = socket(AF_INET, SOCK_DGRAM) 
    sock.settimeout(5.0); 
    sock.sendto("\xff\xff\xff\xff\xff\xff\xff\xff\xff\xffgief", (address, port)) 
    data, addr = sock.recvfrom(1024) 
    sock.close() 
 
    data = data[14:] 
 
    server_name, map_name = data[:-2].split("\x00")[0:2] 
    data = data[-2:] 
    max_players = ord(data[0]) 
    num_players = ord(data[1]) 
 
    return num_players 
 
def tw_get_info(): 
    address = "master.teewars.com" 
    master_port = 8383 
 
    sock = socket(AF_INET, SOCK_DGRAM) 
    sock.settimeout(5.0) 
    sock.sendto("\x20\x00\x00\x00\x00\x48\xff\xff\xff\xffreqt", (address, master_port)) 
 
    data, addr = sock.recvfrom(1024) 
    sock.close() 
    data = data[14:] 
    num_servers = len(data) / 6 
    num_players = 0 
 
    for n in range(0, num_servers): 
        ip = ".".join(map(str, map(ord, data[n*6:n*6+4]))) 
        print ip 
        port = ord(data[n*6+5]) * 256 + ord(data[n*6+4]) 
        try: 
            num_players += tw_get_num_players(ip, port) 
        except: 
            num_servers -= 1 
         
    return (num_servers, num_players)

class TeewarsCommand(Command):
	def __init__(self):
		pass
	
	def trig_twinfo(self, bot, source, target, trigger, argument):
		bot.tell(target, "Teewars servers: %s total players: %s." % tw_get_info())

	def trig_teewars(self, bot, source, target, trigger, argument):
		address = "jp.serp.se"
		port = 8303

		m = re.search("^(\S+)[: ]?(\d*)", argument)

		if m:
			address = m.group(1)
			if m.group(2):
				port = int(m.group(2))

		sock = socket(AF_INET, SOCK_DGRAM)
		sock.sendto("\xff\xff\xff\xff\xff\xff\xff\xff\xff\xffgief", (address, port))
		data, addr = sock.recvfrom(1024)

		data = data[14:]

		server_name, map_name = data[:-2].split("\x00")[0:2]
		data = data[-2:]
		max_players = ord(data[0])
		num_players = ord(data[1])

		bot.tell(target, "Server '%s' at %s:%s is playing %s with %s/%s players." % (server_name, address, port, map_name, num_players, max_players))

