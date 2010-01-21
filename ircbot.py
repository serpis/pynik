import sys
import traceback
import datetime
import plugin_handler
from ircclient import ircclient
from autoreloader.autoreloader import AutoReloader
from heapq import heappush, heappop

# Call plugins_on_load only on first import
try:
	IRCBot
except NameError:
	plugin_handler.plugins_on_load()

class PriorityQueue:
	def __init__(self):
		self.internal_array = []

	def clear(self):
		self.internal_array = []

	def push(self, item):
		heappush(self.internal_array, item)

	def pop(self):
		return heappop(self.internal_array)

	def empty(self):
		return len(self.internal_array) == 0
	
	def top(self):
		return self.internal_array[0]

class TimedEvent:
	def __init__(self, trigger_delta, recurring, target, args):
		self.trigger_delta = trigger_delta
		self.trigger_time = datetime.datetime.now() + trigger_delta
		self.recurring = recurring
		self.target = target
		self.args = args

	def trigger(self):
		self.target(*self.args)

	def reset(self):
		self.trigger_time += self.trigger_delta

	def __cmp__(self, other):
		return cmp(self.trigger_time, other.trigger_time)

class IRCBot(AutoReloader):
	def __init__(self, settings):
		self.settings = settings
		if len(self.settings.networks) > 1:
			raise Exception("Only one network is supported right now.")
		sett = self.settings.networks.values()[0]
		self.client = ircclient.IRCClient(sett['server_address'], sett['server_port'], 
						  sett['nick'], sett['username'], sett['realname'])
		self.client.callbacks = self.callbacks()
		self.plugins = []
		self.timer_heap = PriorityQueue()
		self.need_reload = {}

	def callbacks(self):
		return { "on_connected": self.on_connected, "on_join": self.on_join,
			 "on_nick_change": self.on_nick_change, "on_notice": self.on_notice, 
			 "on_part": self.on_part, "on_privmsg": self.on_privmsg, "on_quit": self.on_quit }

	def is_connected(self):
		return self.client.is_connected()

	def execute_plugins(self, trigger, *arguments):
		for plugin in plugin_handler.all_plugins():
			try:
				#if arguments:
				#	print trigger
				#       print("plugin.%s(self, %s) %s" % (trigger,", ".join(arguments),plugin.__class__ ))
				#else:
				#	print("plugin.%s(self)" % trigger)
				plugin.__class__.__dict__[trigger](plugin, self, *arguments)
			except KeyError:
				pass
			except:
				print "%s: argh", plugin, sys.exc_info(), traceback.extract_tb(sys.exc_info()[2]) % (datetime.datetime.now().strftime("[%H:%M:%S]"))
	
	def on_connected(self):
		for channel in self.settings.networks.values()[0]['channels']:
			try:
				self.join(channel[0], channel[1])
			except IndexError:
				self.join(channel[0])

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

	def on_reload(self):
		# Check for new channels, if so join them
		for channel in self.settings.networks.values()[0]['channels']:
			try:
				self.join(channel[0], channel[1])
			except IndexError:
				self.join(channel[0])

	def reload(self):
		self.need_reload['main'] = True
		self.need_reload['ircbot'] = True

	def reload_plugins(self):
		plugin_handler.plugins_on_unload()
		plugin_handler.reload_plugin_modules()
		plugin_handler.plugins_on_load()
	
	def load_plugin(self, plugin):
		plugin_handler.load_plugin(plugin)

	def connect(self, address, port):
		return self.client.connect(address, port)

	def join(self, channel, password=""):
		return self.client.join(channel, password)

	def send(self, line):
		return self.client.send(line)

	def tell(self, target, message):
		return self.client.tell(target, message)

	def tick(self):
		if self.need_reload.has_key('ircbot') and self.need_reload['ircbot']:
			reload(ircclient)
			reload(plugin_handler)
			self.client.callbacks = self.callbacks()
			self.need_reload['ircbot'] = False

		now = datetime.datetime.now()

		if not self.timer_heap.empty() and not self.client.connected:
			print "ATTENTION! We are not connected. Skipping timers!"
		else:
			while not self.timer_heap.empty() and self.timer_heap.top().trigger_time <= now:
				timer = self.timer_heap.pop()
				timer.trigger()
				if timer.recurring:
					timer.reset()
					self.timer_heap.push(timer)

		self.client.tick()

	def add_timer(self, delta, recurring, target, *args):
		timer = TimedEvent(delta, recurring, target, args)

		self.timer_heap.push(timer)

	def add_background_job(self, name, callback, target, args):
		pass
