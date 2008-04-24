# coding: utf-8

from plugins import Plugin
import re
import utility
import sys
import traceback

class Command(Plugin):
	def can_trigger(self, source, trigger):
		return True

	def on_load(self):
		pass

	def on_unload(self):
		pass

	def get_triggers(self):
		return {}

	def on_command(self, bot, source, target, trigger, arguments):
		triggers = self.get_triggers()

		if trigger in triggers:
			command = triggers[trigger]

			if self.can_trigger(source, trigger):
				m = re.search('^(.+)!', source)
				if m:
					if target == source:
						target = m.group(1)
					source = m.group(1)

				try:
					return utility.timeout(command, 10, (bot, source, target, trigger, arguments))
				except utility.TimeoutException:
					return "Command '%s' took too long to execute." % trigger
				except:
					bot.tell('#botnik', "%s triggered an error by typing \'%s %s\': %s." % (source, trigger, arguments, sys.exc_info()))

					print sys.exc_info()
					print 'Error when executing command \'', trigger, '\':', traceback.extract_tb(sys.exc_info()[2])

					return "Oops. Error logged."
			else:
				return "Bwaha. You can't trigger that!"

		#if trigger in favorites.FavoriteCommands.instance.favorites.keys():
		#	return favorites.FavoriteCommands.instance.trig_fav(bot, source, target, 'fav', trigger + ' ' + arguments)

	def on_privmsg(self, bot, source, target, message):
		p = re.compile('^(\S)(\S+)\s?(.*?)$')

		m = p.match(message)
		
		if m and m.group(1) == '.':
			trigger = m.group(2)
			arguments = m.group(3)

			ret_str = self.on_command(bot, source, target, trigger, arguments)
			if ret_str:
				m = re.search('^(.+)!', source)
				if m:
					if target == source:
						target = m.group(1)
				bot.tell(target, ret_str)
