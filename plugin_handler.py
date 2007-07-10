import os
import sets
import imp
import sys

from copy import copy


prev = copy(sys.modules.values())
from plugins import *
new_modules = []
plugins_module = None

for module in sys.modules.values():
	if module not in prev:
		if module.__name__ == 'plugins':
			plugins_module = module
		
		if module.__name__ == 'plugins.plugins':
			new_modules.insert(0, module)
		elif module.__name__ == 'plugins.commands':
			if len(new_modules) == 0 or new_modules[0].__name__ != 'plugins.plugins':
				new_modules.insert(0, module)
			else:
				new_modules.insert(1, module)
		else:
			new_modules.append(module)

def reload_plugin_modules():
	import traceback
	for module in new_modules:
		try:
			reload(module)
		except:
			print 'error when reloading module', module.__name__, sys.exc_info(), str(traceback.extract_tb(sys.exc_info()[2]))

_instances = {}
	
def get_plugins_by_hook(hook):
	result = []
	for plugin in _instances.values():
		if hook in plugin.hooks:
			result.append(plugin)
	return result

def load_plugin(plugin):
	import re

	package = plugins_module
#	if re.match('^commands\.', plugin):
#		package = commands_module
#		plugin = plugin[9:]

	name = package.__name__ + '.' + plugin
	file, filename, description = imp.find_module(plugin, package.__path__)
	try:
		module = imp.load_module(name, file, filename, description)
		new_modules.append(module)
	except:
		raise
	finally:
		file.close()


def search_for_subclasses(c):
	l = [c]
	for subclass in c.__subclasses__():
		l.extend(search_for_subclasses(subclass))
	return l

def plugins_on_load():
	_instances.clear()
	
	l = search_for_subclasses(plugins.Plugin) 

	for plugin in l:
		_instances[plugin] = plugin()

	for plugin in _instances.values():
		plugin.on_load()

def plugins_on_unload():
	for plugin in _instances.values():
		plugin.on_unload()

	_instances.clear()
