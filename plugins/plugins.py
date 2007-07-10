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
