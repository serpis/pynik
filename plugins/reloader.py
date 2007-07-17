# coding: latin-1

from commands import Command

class ReloadCommand(Command):
	def trig_reload(self, bot, source, target, trigger, argument):
		if source == 'serp' or source == 'teetow':
			bot.reload_plugins()
			bot.tell(target, 'Reloaded and good to go.')
			
class LoadCommand(Command):
	def trig_load(self, bot, source, target, trigger, argument):
		plugin = argument
		if source == 'serp':
			bot.load_plugin(plugin)
			bot.tell(target, 'Plugin ' + plugin + ' loaded. Use \'reload\' to initialize it.')
