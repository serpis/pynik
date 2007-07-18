# coding: latin-1

import sys
import socket
import re
import plugin_handler
import traceback
import errno
import datetime

class Pynik:
	def __init__(self, s=None):
		self.temp_nick_list_channel = None
		self.temp_nick_list = None
		self.nick_lists = {}
		
		if not s:
			self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		else:
			self.s = s

	def connect(self, address, port):
		self.ping_count = 0
		return self.s.connect((address, port))

	def send(self, string):
		return self.s.send(string + "\r\n")

	def tell(self, target, string):
		split = len(string) - 1

		if split >= 400:
			split = 400
			while split > 350:
				if string[split] == ' ':
					break
				split -= 1

			a = string[0:split]
			b = string[split:]
		
			return self.tell(target, a) + self.tell(target, b)
		else:
			return self.send("PRIVMSG " + target + " :" + string)

	def join(self, channel):
		return self.send('JOIN ' + channel)

	def reload_plugins(self):
		plugin_handler.plugins_on_unload()
		plugin_handler.reload_plugin_modules()
		plugin_handler.plugins_on_load()

	def load_plugin(self, plugin):
		plugin_handler.load_plugin(plugin)

	def get_nick(self, host):
		m = re.search('^:?(\S+?)!', host)
		if m:
			return m.group(1)
		else:
			return host

	def on_begin_nick_list(self, tupels):
		m = re.search('. (.+?) :(.*)$', tupels[5])

		if m:
			channel, nicks = m.group(1, 2)

			if self.temp_nick_list_channel != channel:
				self.temp_nick_list_channel = channel
				self.temp_nick_list = []

			for m in re.findall('([^a-zA-Z\[\]{}]?)(.+?)(\s|$)', nicks):
				prefix, nick = m[0:2]

				self.temp_nick_list.append(nick)
			
	def on_end_nick_list(self, tupels):
		self.nick_lists[self.temp_nick_list_channel] = self.temp_nick_list
		self.temp_nick_list_channel = None
		self.temp_nick_list = None

	def on_join(self, tupels):
		source, channel = [tupels[1], tupels[4]]

		source_nick = self.get_nick(source)

		if not channel in self.nick_lists:
			self.nick_lists[channel] = []

		self.nick_lists[channel].append(source_nick)

	def on_kick(self, tupels):
		source, channel = [tupels[1], tupels[4]]
		target_nick = None

		m = re.search('^([^ ]+)', tupels[5])
		if m:
			target_nick = m.group(1)

		if target_nick:
			for nick_list in self.nick_lists.values():
				if target_nick in nick_list:
					nick_list.remove(target_nick)

	def on_nick(self, tupels):
		source, new_nick = [tupels[1], tupels[4]]

		source_nick = self.get_nick(source)

		for nick_list in self.nick_lists.values():
			if source_nick in nick_list:
				nick_list.remove(source_nick)
				nick_list.append(new_nick)

	def on_part(self, tupels):
		source, channel, reason = [tupels[1], tupels[4], tupels[5]]

		source_nick = self.get_nick(source)

		for nick_list in self.nick_lists.values():
			if source_nick in nick_list:
				nick_list.remove(source_nick)

	def on_quit(self, tupels):
		source = tupels[1]
		reason = tupels[4]

		if tupels[5] != '':
			reason += ' ' + tupels[5]

		source_nick = self.get_nick(source)

		for nick_list in self.nick_lists.values():
			if source_nick in nick_list:
				nick_list.remove(source_nick)

	def on_ping(self, tupels):
		self.send("PONG :" + tupels[4])

		for plugin in plugin_handler.get_plugins_by_hook('on_ping'):
			plugin.on_ping(tupels)

		if self.ping_count == 0:
			self.on_connected(tupels)

		self.ping_count += 1

	def on_privmsg(self, tupels):
		#reload(plugins)
	
		source = tupels[2]
		target = tupels[4]

		if target[0] != '#':
			target = source

		for plugin in plugin_handler.get_plugins_by_hook('on_privmsg'):
			plugin.on_privmsg(self, source, target, tupels)
	
	def on_notice(self, tupels):
		for plugin in plugin_handler.get_plugins_by_hook('on_notice'):
			plugin.on_notice(tupels)

	def on_connected(self, tupels):
		for plugin in plugin_handler.get_plugins_by_hook('on_connected'):
			plugin.on_connected(self, 'irc.server.address')

	def on_error(self, tupels):
		print 'the irc server informs of an error: ' + tupels[5]

	def timer_beat(self, now):
		for plugin in plugin_handler.all_plugins():
			plugin.timer_beat(self, now)

	def run(self):
		irc_message_pattern = re.compile('^(:([^  ]+))?[   ]*([^  ]+)[  ]+:?([^  ]*)[   ]*:?(.*)$')
		irc_message_match = irc_message_pattern.match
		message_handlers = {
			'JOIN': self.on_join,
			'KICK': self.on_kick,
			'NICK': self.on_nick,
			'PART': self.on_part,
			'QUIT': self.on_quit,
			'PING': self.on_ping,
			'PRIVMSG': self.on_privmsg,
			'NOTICE': self.on_notice,
			'ERROR': self.on_error,
			'353': self.on_begin_nick_list,
			'366': self.on_end_nick_list,
		}
		recv_buf = ''

		next_beat = None

		while True:
			try:
				self.s.settimeout(1)
				retn = self.s.recv(1024)
				self.s.settimeout(None)

				if len(retn) <= 0:
					raise Exception('error while receiving')
		
				recv_buf += retn
				recv_lines = recv_buf.splitlines(True)
				recv_buf = ''
				for line in recv_lines:
					if not line.endswith("\r\n"):
						recv_buf = line
					else:
						m = irc_message_match(line.rstrip("\r\n"))
						if m:
							try:
								if m.group(3) in message_handlers:
									message_handlers[m.group(3)](m.group(0, 1, 2, 3, 4, 5))
							except:
								print 'OMG FUCKING FAIL IN PLUGIN!!', sys.exc_info(), traceback.extract_tb(sys.exc_info()[2])
			except socket.timeout:
				self.s.settimeout(None)

			now = datetime.datetime.now()
	
			if not next_beat or next_beat < now:
				next_beat = now + datetime.timedelta(0, 1)
	
				try:
					self.timer_beat(now)
				except:
					print 'OMG FUCKING FAIL IN TIMER_BEAT!!', sys.exc_info(), traceback.extract_tb(sys.exc_info()[2])

plugin_handler.plugins_on_load()

if __name__ == "__main__":
	try_again = True
	while try_again:
		try_again = False

		p = Pynik()
		p.connect("fi.quakenet.org", 6667)
		p.send("USER pynik . . :pynik")
		p.send("NICK pynik-test")
		try:
			p.run()
		except KeyboardInterrupt:
			raise
		except:
			print 'A very big error came by and said', sys.exc_info(), traceback.extract_tb(sys.exc_info()[2])
			try_again = True
