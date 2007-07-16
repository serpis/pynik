# coding: latin-1

from commands import Command

class ExampleCommand(Command):
	def __init__(self):
		pass
	
	def trig_example(self, bot, source, target, trigger, argument):
		if target[0] == '#': # is the first character in target a #? then, it's a channel!
			bot.tell(target, 'Ohayou! ' + target + ' is a channel with these users: ' + str(bot.nick_lists[target]) + '!')
