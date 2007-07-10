# coding: latin-1

from commands import Command

class ReloadCommand(Command):
	triggers = ['reload']

	def __init__(self):
		pass
	
	def on_trigger(self, bot, source, target, trigger, argument):
		if source == 'serp' or source == 'teetow':
			bot.reload_plugins()
			bot.tell(target, 'Reloaded and good to go.')
			
class LoadCommand(Command):
	triggers = ['load']

	def __init__(self):
		pass
	
	def on_trigger(self, bot, source, target, trigger, argument):
		plugin = argument
		if source == 'serp':
			bot.load_plugin(plugin)
			bot.tell(target, 'Plugin ' + plugin + ' loaded. use \'reload\' to initialize it.')
