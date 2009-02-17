from ircclient.ircclient import IRCClient
import plugin_handler
import sys
import traceback
import datetime

plugin_handler.plugins_on_load()

from heapq import heappush, heappop
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

class IRCBot:
	def __init__(self, address, port, nick, username, realname):
		self.client = IRCClient(address, port, nick, username, realname)
		self.client.callbacks = { "on_connected": self.on_connected, "on_join": self.on_join, "on_nick_change": self.on_nick_change, "on_notice": self.on_notice, "on_part": self.on_part, "on_privmsg": self.on_privmsg, "on_quit": self.on_quit }
		self.plugins = []
		self.timer_heap = PriorityQueue()

	def is_connected(self):
		return self.client.is_connected()

	def execute_plugins(self, trigger, *arguments):
		for plugin in plugin_handler.all_plugins():
			try:
				#if arguments:
				#	print trigger
				#	print("plugin.%s(self, %s)" % (trigger,", ".join(arguments)))
				#else:
				#	print("plugin.%s(self)" % trigger)
				plugin.__class__.__dict__[trigger](plugin, self, *arguments)
			except KeyError:
				pass
			except:
				print "argh", plugin, sys.exc_info(), traceback.extract_tb(sys.exc_info()[2])
	
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
		#for plugin in plugin_handler.all_plugins():
		#	plugin.on_privmsg(self, nick, target, message)
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
