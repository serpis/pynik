from plugins import Plugin
import __main__
#//from __main__ import *

class Command(Plugin):
	triggers = []

	def __repr__(self):
		return '<%s %r>' % (
			self.__class__.__name__,
			self.triggers
		)

	def on_trigger(self, bot, source, returner, trigger, argument):
		raise Exception('on_trigger not implemented')

	def on_load(self):
		pass

	def on_unload(self):
		pass

def get_commands_by_trigger(trigger):
	commands = []

	for command in Command.__subclasses__():
		cmd = __main__.plugin_instances()[command]
		if trigger in cmd.triggers:
			commands.append(cmd)

	return commands
