# coding: utf-8

from commands import Command

class ExampleCommand(Command):
	def __init__(self):
		pass
	
	def trig_example(self, bot, source, target, trigger, argument):
		# This plugin does not work anymore.
		if target[0] == '#': # is the first character in target a #? then, it's a channel!
			#print bot.nick_lists[target]
			return "Ohayou %s! %s is a channel with %s users!" % (source, target, "a number of")
