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

	def timer_beat(self, bot, now, network, **kwargs):
		""" Called every second. """
		pass

	def on_connected(self, bot, network, **kwargs):
		""" Called when an ircclient is connected to an IRC-server. """
		pass

	def on_join(self, bot, nick, channel, network, **kwargs):
		""" Called when an ircclient joins a new channel. """
		pass

	def on_nick_changed(self, bot, old_nick, new_nick, network, **kwargs):
		""" Called when an ircclient receives a NICK change. """
		pass
		
	def on_notice(self, bot, source, target, message, network, **kwargs):
		""" Called when an ircclient receives a NOTICE. """
		pass

	def on_part(self, bot, nick, channel, reason, network, **kwargs):
		""" Called when an ircclient receives a PART. """
		pass

	def on_privmsg(self, bot, source, target, message, network, **kwargs):
		""" Called when an ircclient receives a PRIVMSG. """
		pass
		
	def on_quit(self, bot, nick, reason, network, **kwargs):
		""" Called when an ircclient receives a QUIT. """
		pass

