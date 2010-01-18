# coding: utf-8

class Plugin(object):
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

	def on_connected(self, bot):
		pass

	def on_join(self, bot, nick, channel):
		pass

	def on_nick_changed(self, bot, old_nick, new_nick):
		pass
		
	def on_notice(self, bot, source, target, message):
		pass

	def on_part(self, bot, nick, channel, reason):
		pass

	def on_privmsg(self, bot, source, target, message):
		pass
		
	def on_quit(self, bot, nick, reason):
		pass

