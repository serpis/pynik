from ircclient.ircclient import IRCClient
import plugin_handler
import sys
import traceback
import datetime

plugin_handler.plugins_on_load()

class OfflineTester:
	def __init__(self):
		pass

	def execute_plugins(self, trigger, *arguments):
		for plugin in plugin_handler.all_plugins():
			try:
				plugin.__class__.__dict__[trigger](plugin, self, *arguments)
			except KeyError:
				pass
			except:
				print "argh", plugin, sys.exc_info(), traceback.extract_tb(sys.exc_info()[2])
	
	def on_privmsg(self, nick, target, message):
		self.execute_plugins("on_privmsg", nick, target, message)

	def reload_plugins(self):
		plugin_handler.plugins_on_unload()
		plugin_handler.reload_plugin_modules()
		plugin_handler.plugins_on_load()
	
	def load_plugin(self, plugin):
		plugin_handler.load_plugin(plugin)

	def tell(self, target, message):
		print "telling %s: %s" % (target, message)

tester = OfflineTester()
print "all right. let's go!"
while 1:
	print "> ",
	line = sys.stdin.readline()
	if not line:
		break
	while len(line) > 0 and (line[-1] == '\n' or line[-1] == '\r'):
		line = line.rstrip("\r")
		line = line.rstrip("\n")
	tester.on_privmsg("serp", "#testchannel", line);

