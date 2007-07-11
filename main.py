# coding: latin-1

import sys
import socket
import re
import plugin_handler
import traceback

class Pynik:
	p = re.compile('^(:([^  ]+))?[   ]*([^  ]+)[  ]+:?([^  ]*)[   ]*:?(.*)$')
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	recv_buf = ''

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

		p = re.compile('^(.+)!')
		m = p.match(source)	
		if m:
			source = m.group(1)

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

	def run(self):
		while True:
			retn = self.s.recv(1024)
	
			if len(retn) <= 0:
				print 'error while receiving'
				break
	
			self.recv_buf += retn

			while True:
				index = self.recv_buf.find("\r\n")
				if index < 0:
					break

				line = self.recv_buf[0:index]
				self.recv_buf = self.recv_buf[index+2:]

				m = self.p.match(line)
				if m:
					pairs = {
						'PING': self.on_ping,
						'PRIVMSG': self.on_privmsg,
						'NOTICE': self.on_notice,
						'ERROR': self.on_error
					}

					try:
						if m.group(3) in pairs:
							pairs[m.group(3)](m.group(0, 1, 2, 3, 4, 5))
					except:
						print 'OMG FUCKING FAIL IN PLUGIN!!', sys.exc_info(), traceback.extract_tb(sys.exc_info()[2])

plugin_handler.plugins_on_load()

p = Pynik()
p.connect("se.quakenet.org", 6667)
p.send("USER pynik . . :pynik")
p.send("NICK pynik")
p.run()
