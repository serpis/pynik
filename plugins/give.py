# coding: utf-8

from commands import Command
import re

class GiveCommand(Command):
	def trig_give(self, bot, source, target, trigger, argument):		
		m = re.search("(\S+) +(\S+) ?(.*)$", argument)
		if m:
			hilight, give_trig, give_args = m.groups()

			#ret_str = command_catcher.CommandCatcherPlugin.instance.on_command(bot, source, target, give_trig, give_args)
			ret_str = ".."

			if ret_str:
				return "%s: %s" % (hilight, ret_str)
			else:
				return "Nothing to give :<"
