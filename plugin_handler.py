import os
import sets
import imp
import sys
import re

from copy import copy

prev = copy(sys.modules.values())
from plugins import *
new_modules = []
plugins_module = None

for module in sys.modules.values():
	if not module:
		continue
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

new_modules = filter(lambda x: re.match('^plugins\.', x.__name__), new_modules)

def reload_plugin_modules():
	import traceback
	for module in new_modules:
		try:
			reload(module)
		except:
			print 'error when reloading module', module.__name__, sys.exc_info(), str(traceback.extract_tb(sys.exc_info()[2]))

def search_for_subclasses(c):
	l = [c]
	for subclass in c.__subclasses__():
		l.extend(search_for_subclasses(subclass))
	return l
	
def get_plugins_by_hook(hook):
	result = []
	for plugin in search_for_subclasses(plugins.Plugin):
		if hook in plugin.hooks:
			result.append(plugin.instance)
	return result

def all_plugins():
	result = []
	for plugin in search_for_subclasses(plugins.Plugin):
		result.append(plugin.instance)
	return result

def load_plugin(plugin):
	import re

	package = plugins_module

	name = package.__name__ + '.' + plugin
	file, filename, description = imp.find_module(plugin, package.__path__)
	try:
		module = imp.load_module(name, file, filename, description)
		new_modules.append(module)
	except:
		raise
	finally:
		file.close()

def plugins_on_load():
	l = search_for_subclasses(plugins.Plugin) 

	for plugin in l:
		plugin.instance = plugin()

	for plugin in l:
		plugin.instance.on_load()

def plugins_on_unload():
	l = search_for_subclasses(plugins.Plugin) 

	for plugin in l:
		plugin.instance.on_unload()

	for plugin in l:
		plugin.instance = None
