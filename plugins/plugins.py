# coding: utf-8

class Plugin(object):
	hooks = []

	def __repr__(self):
		return '<%s %r>' % (
			self.__class__.__name__,
			self.hooks
		)

	def on_load(self):
		pass

	def on_unload(self):
		pass

	def get_options(self):
		return []

	def on_modified_options(self):
		pass

	def timer_beat(self, bot, now):
		pass

	def on_privmsg(self, bot, source, target, tupels):
		pass
	
	def on_notice(self, bot, source, target, tupels):
		pass

	def on_connected(self, bot, address):
		pass
