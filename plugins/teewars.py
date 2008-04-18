# coding: utf-8

from __future__ import with_statement
from commands import Command
import time
import re
from socket import *

from socket import * 
from struct import * 
import datetime
import utility
import thread
import sys
import traceback

list_lock = thread.allocate_lock()

def tw_get_num_players(address, port):
	sock = socket(AF_INET, SOCK_DGRAM) 
	sock.settimeout(5.0); 
	sock.sendto("\xff\xff\xff\xff\xff\xff\xff\xff\xff\xffgief", (address, port)) 
	data, addr = sock.recvfrom(1024) 
	sock.close() 
 
	data = data[14:] 
 
	slots = data.split("\x00")
	server_info = slots[0:8]
	server_name, map_name = slots[1:3]
	data = data[-2:] 
	num_players, max_players = map(int, slots[6:8])

	return num_players, max_players

def tw_get_num_players_proxy(address, port, players_dic):
	try:
		num_players, max_players = tw_get_num_players(address, port)

		with list_lock:
			players_dic[thread.get_ident()] = num_players
	except:
		#print 'exception O.o', sys.exc_info(), traceback.extract_tb(sys.exc_info()[2])
		with list_lock:
			players_dic[thread.get_ident()] = -1

def tw_get_info(): 
	counter = 0
	address = "master.teewars.com" 
	master_port = 8300
 
	sock = socket(AF_INET, SOCK_DGRAM) 
	sock.settimeout(5.0) 
	sock.sendto("\x20\x00\x00\x00\x00\x00\xff\xff\xff\xffreqt", (address, master_port)) 
 
	try:
		data, addr = sock.recvfrom(1024) 
		sock.close() 
		data = data[14:] 
		num_servers = len(data) / 6 
		num_players = 0 

		players_dic = {}

		for n in range(0, num_servers): 
			ip = ".".join(map(str, map(ord, data[n*6:n*6+4]))) 
			port = ord(data[n*6+5]) * 256 + ord(data[n*6+4]) 

			#print ip, port

			with list_lock:
				id = thread.start_new_thread(tw_get_num_players_proxy, (ip, port, players_dic))
				players_dic[id] = -2

		while True:
			has_items = False
			with list_lock:
				for slot in players_dic.keys():
					if players_dic[slot] == -2:
						has_items = True
						break

			if has_items:
				time.sleep(0.5)
			else:
				break

		players_list = []

		for slot in players_dic.keys():
			if players_dic[slot] != -1:
				players_list.append(players_dic[slot])

		num_servers = len(players_list)
		num_players = reduce(lambda x, y: x + y, players_list)

		with open("data/tw_stats.txt", "a") as file:
			file.write("%s %s %s\n" % (int(time.time()), num_servers, num_players))
			 
		utility.read_url("http://serp.starkast.net/berserker/gief_stats.php?timestamp=%s&servers=%s&players=%s" % (int(time.time()), num_servers, num_players));
		return (num_servers, num_players)
	except:
		print 'exception O.o', sys.exc_info(), traceback.extract_tb(sys.exc_info()[2])
		return None

class TeewarsCommand(Command):
	def __init__(self):
		self.next_beat = None
		self.cached_info = None
	
	def trig_twinfo(self, bot, source, target, trigger, argument):
		self.cached_info = tw_get_info()
		if self.cached_info:
			return "There are currently %s public Teewars servers with a total of %s players." % self.cached_info
		else:
			return "I don't have any stats yet... Please wait a minute! :-)"

	def trig_teewars(self, bot, source, target, trigger, argument):
		address = "jp.serp.se"
		port = 8303

		m = re.search("^(\S+)[: ]?(\d*)", argument)

		if m:
			address = m.group(1)
			if m.group(2):
				port = int(m.group(2))

		num_players, max_players = tw_get_num_players(address, port)

		return "Server has %d/%d players." % (num_player, max_players)
		#return "Server '%s' at %s:%s is playing %s with %s/%s players." % (server_name, address, port, map_name, num_players, max_players)

	def timer_beat(self, bot, now):
		if not self.next_beat or self.next_beat < now:
			self.next_beat = now + datetime.timedelta(0, 0, 0, 0, 2)
			info = tw_get_info()
			if info:
				self.cached_info = info
