import re
import sys
import traceback
import datetime
from copy import copy
from heapq import heappush, heappop
from autoreloader.autoreloader import AutoReloader

import plugin_handler
from ircclient import ircclient

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
		self.callbacks = self.get_callbacks()
		self.clients = {}
		self.networks = []
		self.plugins = []
		self.timer_heap = PriorityQueue()
		self.need_reload = {}

		for network in self.settings.networks:
			net_settings = self.settings.networks[network]
			print "Connecting to network %s at %s:%s..." % (network,
			      net_settings['server_address'], net_settings['server_port'])
			self.clients[network] = ircclient.IRCClient(net_settings['server_address'],
								    net_settings['server_port'],
								    net_settings['nick'],
								    net_settings['username'],
								    net_settings['realname'],
								    network,
								    net_settings.setdefault('server_password'))
			self.clients[network].callbacks = copy(self.callbacks)
			self.networks.append(network)

	def get_callbacks(self):
		return { "on_connected": self.on_connected, "on_join": self.on_join,
			 "on_nick_change": self.on_nick_change, "on_notice": self.on_notice, 
			 "on_part": self.on_part, "on_privmsg": self.on_privmsg, "on_quit": self.on_quit }

	def is_connected(self, network=None):
		if network == None:
			raise DeprecationWarning("network parameter missing")			
		return self.clients['networks'].is_connected()

	def execute_plugins(self, network, trigger, *arguments):
		for plugin in plugin_handler.all_plugins():
			try:
				if plugin.__class__.__dict__.has_key(trigger):
					# FIXME this is rather ugly, for compatiblity with pynik
					if plugin.__class__.__dict__[trigger].func_code.co_argcount == len(arguments) + 2:
						plugin.__class__.__dict__[trigger](plugin, self, *arguments) # Call without network
					elif plugin.__class__.__dict__[trigger].func_code.co_argcount == len(arguments) + 3:
						plugin.__class__.__dict__[trigger](plugin, self, *arguments, **{'network': network})
					else:
						raise NotImplementedError("Plugin '%s' argument count missmatch, was %s." % (
								plugin, plugin.__class__.__dict__[trigger].func_code.co_argcount))
			except:
				print "%s %s Plugin '%s' threw exception, exinfo: '%s', traceback: '%s'" % (
					datetime.datetime.now().strftime("[%H:%M:%S]"), network,
					plugin, sys.exc_info(), traceback.extract_tb(sys.exc_info()[2]))

				if trigger != "timer_beat":
					try:
						self.tell(self.settings.admin_network, self.settings.admin_channel,
							  "%s %s Plugin '%s' threw exception, exinfo: '%s', traceback: '%s'" % (
								datetime.datetime.now().strftime("[%H:%M:%S]"), network,
								plugin, sys.exc_info(), traceback.extract_tb(sys.exc_info()[2])[::-1]))
					except:
						print "%s %s Unable to send exception to admin channel, exinfo: '%s', traceback: '%s'" % (
							datetime.datetime.now().strftime("[%H:%M:%S]"), network,
							sys.exc_info(), traceback.extract_tb(sys.exc_info()[2]))

	def on_connected(self, network):
		for channel in self.settings.networks[network]['channels']:
			try:
				self.join(network, channel[0], channel[1])
			except IndexError:
				self.join(network, channel[0])

		self.execute_plugins(network, "on_connected")

	def on_join(self, network, nick, channel):
		self.execute_plugins(network, "on_join", nick, channel)

	def on_nick_change(self, network, old_nick, new_nick):
		self.execute_plugins(network, "on_nick_change", old_nick, new_nick)

	def on_notice(self, network, nick, target, message):
		self.execute_plugins(network, "on_notice", nick, target, message)

	def on_part(self, network, nick, channel, reason):
		self.execute_plugins(network, "on_part", nick, channel, reason)

	def on_privmsg(self, network, nick, target, message):
		self.execute_plugins(network, "on_privmsg", nick, target, message)

	def on_quit(self, network, nick, reason):
		self.execute_plugins(network, "on_quit", nick, reason)

	def on_reload(self):
		# Check for new channels, if so join them
		for network in self.networks:
			for channel in self.settings.networks[network]['channels']:
				try:
					self.join(network, channel[0], channel[1])
				except IndexError:
					self.join(network, channel[0])

		# Connect to new networks
		for network in self.settings.networks:
			if network not in self.networks:
				net_settings = self.settings.networks[network]
				print "Connecting to new network %s at %s:%s..." % (network,
				      net_settings['server_address'], net_settings['server_port'])
				self.clients[network] = ircclient.IRCClient(net_settings['server_address'],
									    net_settings['server_port'],
									    net_settings['nick'],
									    net_settings['username'],
									    net_settings['realname'],
									    network)
				self.clients[network].callbacks = copy(self.callbacks)
				self.networks.append(network)

	def reload(self):
		self.need_reload['main'] = True
		self.need_reload['ircbot'] = True

	def reload_plugins(self):
		plugin_handler.plugins_on_unload()
		plugin_handler.reload_plugin_modules()
		plugin_handler.plugins_on_load()
	
	def load_plugin(self, plugin):
		plugin_handler.load_plugin(plugin)

	def join(self, network, channel, password=""):
		return self.clients[network].join(channel, password)

	def send(self, network, line=None):
		if line == None:
			raise DeprecationWarning("network parameter missing")
		return self.clients[network].send(line)

	def send_all_networks(self, line):
		for client in self.clients.values():
			if client.is_connected():
				client.send(line)

	def tell(self, network, target, message=None):
		if message == None:
			raise DeprecationWarning("network parameter missing")
		return self.clients[network].tell(target, message)

	def tick(self):
		if self.need_reload.has_key('ircbot') and self.need_reload['ircbot']:
			reload(ircclient)
			reload(plugin_handler)
			self.callbacks = self.get_callbacks()
			for client in self.clients.values():
				client.callbacks = copy(self.callbacks)
				#client.on_reload()
			#self.execute_plugins(, "")


			self.need_reload['ircbot'] = False

		# FIXME timer is broken
#		if not self.timer_heap.empty() and not self.client.connected:
#			print "ATTENTION! We are not connected. Skipping timers!"
#		else:
		now = datetime.datetime.now()
		while not self.timer_heap.empty() and self.timer_heap.top().trigger_time <= now:
			timer = self.timer_heap.pop()
			timer.trigger()
			if timer.recurring:
				timer.reset()
				self.timer_heap.push(timer)

		for client in self.clients.values():
			client.tick()

		# Call timer_beat in all networks
		for network in self.networks:
			self.execute_plugins(network, "timer_beat", now)

	def add_timer(self, delta, recurring, target, *args):
		timer = TimedEvent(delta, recurring, target, args)

		self.timer_heap.push(timer)

	def add_background_job(self, name, callback, target, args):
		pass
