# coding: utf-8

from plugins import Plugin

class Command(Plugin):
	triggers = []

	def __repr__(self):
		return '<%s %r>' % (
			self.__class__.__name__,
			self.triggers
		)

	def on_trigger(self, bot, source, returner, trigger, argument):
		raise Exception('on_trigger not implemented')

	def can_trigger(self, source, trigger):
		return True

	def on_load(self):
		pass

	def on_unload(self):
		pass

def get_commands_by_trigger(trigger):
	commands = []

	for command in Command.__subclasses__():
		if trigger in command.triggers:
			commands.append(command.instance)

	return commands
