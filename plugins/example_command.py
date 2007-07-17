# coding: latin-1

from commands import Command

class ExampleCommand(Command):
	def __init__(self):
		pass
	
	def trig_example(self, bot, source, target, trigger, argument):
		if target[0] == '#': # is the first character in target a #? then, it's a channel!
			pass
			#bot.tell(target, "Ohayou %s! %s is a channel with %s users: %s!" % (source, target, len(bot.nick_lists[target]), bot.nick_lists[target]))


command = ExampleCommand()

command.trig_example(None, 'dk', '#c++.se', 'example', 'huh?')
