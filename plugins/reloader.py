# coding: utf-8

from commands import Command

def get_plugins():
	return [ReloadCommand(), LoadCommand()]

class ReloadCommand(Command):
	def get_triggers(self):
		return { "reload": self.trig_reload }

	def trig_reload(self, bot, source, target, trigger, argument):
		if source == 'serp' or source == 'teetow':
			bot.reload_plugins()
			return "Reloaded and good to go!"
			
class LoadCommand(Command):
	def get_triggers(self):
		return { "load": self.trig_load }

	def trig_load(self, bot, source, target, trigger, argument):
		plugin = argument
		if source == 'serp' or source == 'teetow':
			bot.load_plugin(plugin)
			return "Plugin %s loaded. Use 'reload' to initialize it." % plugin
