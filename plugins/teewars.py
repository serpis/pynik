# coding: latin-1

from __future__ import with_statement
from commands import Command
import re
from socket import *

class TeewarsCommand(Command):
	def __init__(self):
		pass

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

		bot.tell(target, "Server '%s' at %s:%s has %s/%s players." % (server_name, address, port, num_players, max_players))

