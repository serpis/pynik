from ircclient.ircclient import IRCClient
import plugin_handler
import sys
import traceback

plugin_handler.plugins_on_load()

class IRCBot():
	def __init__(self):
		self.client = IRCClient()
		self.client.callbacks = { "on_connected": self.on_connected, "on_join": self.on_join, "on_nick_change": self.on_nick_change, "on_notice": self.on_notice, "on_part": self.on_part, "on_privmsg": self.on_privmsg, "on_quit": self.on_quit }
		self.plugins = []

	def execute_plugins(self, trigger, *arguments):
		for plugin in plugin_handler.get_plugins_by_hook(trigger):
			try:
				plugin.__class__.__dict__[trigger](plugin, self, *arguments)
			except:
				print "argh", sys.exc_info(), traceback.extract_tb(sys.exc_info()[2])
	
	def on_connected(self):
		self.execute_plugins("on_connected")

	def on_join(self, nick, channel):
		self.execute_plugins("on_join", nick, channel)

	def on_nick_change(self, old_nick, new_nick):
		self.execute_plugins("on_nick_change", old_nick, new_nick)

	def on_notice(self, nick, target, message):
		self.execute_plugins("on_notice", nick, target, message)

	def on_part(self, nick, channel, reason):
		self.execute_plugins("on_part", nick, channel, reason)

	def on_privmsg(self, nick, target, message):
		self.execute_plugins("on_privmsg", nick, target, message)

	def on_quit(self, nick, reason):
		self.execute_plugins("on_quit", nick, reason)


	def reload_plugins(self):
		plugin_handler.plugins_on_unload()
		plugin_handler.reload_plugin_modules()
		plugin_handler.plugins_on_load()
	
	def load_plugin(self, plugin):
		plugin_handler.load_plugin(plugin)


	def connect(self, address, port):
		return self.client.connect(address, port)

	def join(self, channel):
		return self.client.join(channel)

	def send(self, line):
		return self.client.send(line)

	def tell(self, target, message):
		return self.client.tell(target, message)

	def tick(self):
		self.client.tick()

