# coding: utf-8

from commands import Command

class ReloadCommand(Command):
	def trig_reload(self, bot, source, target, trigger, argument):
		if source == 'serp' or source == 'teetow':
			bot.reload_plugins()
			return "Reloaded and good to go!"
			
class LoadCommand(Command):
	def trig_load(self, bot, source, target, trigger, argument):
		plugin = argument
		if source == 'serp' or source == 'teetow':
			bot.load_plugin(plugin)
			return "Plugin %s loaded. Use 'reload' to initialize it." % plugin
