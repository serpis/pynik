# coding: utf-8

import re
import sys
from plugins import Plugin
import favorites
import commands
import utility
import traceback
import settings

class CommandCatcherPlugin(Plugin): 
	hooks = ['on_privmsg']   

	def __init__(self):
		pass

	def on_command(self, bot, source, target, trigger, arguments):
		meth_name = 'trig_' + trigger.lower()
		pairs = []
		
		for command_class in commands.Command.__subclasses__():
			import __builtin__
			meth = None
			try:
				meth = command_class.instance.__getattribute__(meth_name)
				pairs.append([command_class.instance, meth])
			except:
				pass
				
		for command in commands.get_commands_by_trigger(trigger):
			pairs.append([command, command.on_trigger])

		for pair in pairs:
			command, method = pair

			if command.can_trigger(source, trigger):
				m = re.search('^(.+)!', source)
				if m:
					if target == source:
						target = m.group(1)
					source = m.group(1)

				try:
					return utility.timeout(method, 10, (bot, source, target, trigger, arguments))
				except utility.TimeoutException:
					return "Command '%s' took too long to execute." % trigger
				except MemoryError:
					return "Command '%s' used to much memory." % trigger
				except:
					bot.tell(settings.admin_channel, 
						 "%s triggered an error by typing '%s %s': %s, tb: %s." % (source, trigger, 
						 arguments, sys.exc_info(), traceback.extract_tb(sys.exc_info()[2])[-1] ))
					
					print "Error triggered by '%s' with command '%s', exinfo: '%s', traceback: '%s'" % (source, 
					      trigger, sys.exc_info(), traceback.extract_tb(sys.exc_info()[2]))
					return "Oops. Error logged."
			else:
				return "Bwaha. You can't trigger that!"

		if not len(pairs):
			if trigger in favorites.FavoriteCommands.instance.favorites.keys():
				return favorites.FavoriteCommands.instance.trig_fav(bot, source, target, 'fav', trigger + ' ' + arguments)
	
	def on_privmsg(self, bot, source, target, message):
		m = re.match(r'^(\S)((\S+)\s?(.*?))$', message)
		if m and m.group(1) == '.':
			body = m.group(2)
			if body[0] == '(':
				trigger = "lisp"
				arguments = body
			else:
				trigger = m.group(3)
				arguments = m.group(4)

			ret_str = self.on_command(bot, source, target, trigger, arguments)
			if ret_str:
				m = re.search('^(.+)!', source)
				if m:
					if target == source:
						target = m.group(1)
				
				bot.tell(target, ret_str)


	def on_load(self):
		pass
		
	def on_unload(self):
		pass
