# coding: utf-8

from commands import Command
from plugins import Plugin
import re
import sys
import utility

class OptionsCommand(Command):
	_table = {}

	def __init__(self):
		pass
	
	def trig_options(self, bot, source, target, trigger, argument):
		if utility.has_admin_privileges(source, target):
			self.on_message(bot, source, target, trigger, argument)

	def on_message(self, bot, source, target, trigger, argument):
		m = re.search('^(\w*)\.?(\w*)\.?(\w*)\(?(.*?)\)?$', argument)

		if m:
			module_name, option_name, method_name, method_args = m.group(1, 2, 3, 4)

			name = ''
		
			modules = self.get_members_by_name(self._table.keys(), module_name)
			if not len(module_name) or len(modules) > 1:
				return "Choose a module: %s." % ", ".join(modules) 
			elif len(modules) == 1:
				module_name = modules[0]
				module = self._table[module_name]
				name = module_name

				plugin = None

				for p in utility.get_all_subclasses(Plugin):
					if p.__name__ == module_name:
						plugin = p.instance
						break
				
				options = self.get_members_by_name(module, option_name)
				if not len(option_name) or len(options) > 1:
					return "You're at: %s. Choose an option: %s." % (name, ", ".join(options))
				elif len(options) == 1:
					option_name = options[0]
					option = module[option_name]
					obj = plugin.__getattribute__(option_name)
					name += '.' + option_name

					methods = self.get_members_by_name(option, method_name)
					if not len(method_name) or len(methods) > 1:
						return 'You\'re at: ' + name + '. Choose a method: ' + ', '.join(methods) + '.'
					elif len(methods) == 1:
						method_name = methods[0]
						method = option[method_name]

						if method == self.dict_print or method == self.list_print:
							return 'Contents of \'' + option_name + '\': ' + method(obj) + '.'
						elif method == self.dict_assign:
							m = re.search('^\s*\'?"?(.+?)\'?"?,\s*\'?"?(.+?)\'?"?\s*$', method_args)
							if m:
								a = m.groups()
								#return 'args: |' + a[0] + '|' + a[1] + '|')
								method(obj, a[0], a[1])
								return 'All done, as far as I know.'
							else:
								return 'Couldn\'t parse argument(s).'
						else:
							m = re.search('^\s*\'?"?(.+?)\'?"?\s*$', method_args)
							if m:
								a = m.groups()
	
								method(obj, a[0])
								return 'All done, as far as I know.'
							else:
								return 'Couldn\'t parse argument(s).'

						plugin.on_modified_options()

					else:
						return 'Couldn\'t find method \'' + method_name + '\' in ' + name + '.'
				else:
					return 'Couldn\'t find option \'' + option_name + '\' in ' + name + '.'
			else:
				return 'Couldn\'t find module \'' + module_name + '\'.'

	def get_nodes_from_scratch(self, stratch):
		modules = {}

		for module in utility.get_all_subclasses(Plugin):
			name = module.__name__
			modules[name] = module

		return modules

	def get_nodes_from_module(self, module):
		options = {}

		instance = module.instance

		for opt in instance.get_options():
			options[opt] = instance.__getattribute__(opt)

		return options

	def dict_print(self, d):
		return ', '.join(sorted(d.keys()))

	def dict_assign(self, d, k, v):
		d[k] = v

	def dict_remove(self, d, k):
		del d[k]

	def list_print(self, l):
		return ', '.join(sorted(l))

	def list_append(self, l, v):
		l.append(v)

	def list_remove(self, l, v):
		l.remove(v)

	def str_print(self, s):
		return s

	def str_set(self, s, v):
		s = v

	def get_nodes_from_option(self, option):
		methods = {}

		names = {
			dict: {'assign': self.dict_assign, 'remove': self.dict_remove, 'print': self.dict_print},
			list: {'append': self.list_append, 'remove': self.list_remove, 'print': self.list_print},
			str: {'set': self.str_set, 'print': self.str_print}
		}[option.__class__]

	  	return names

	def build_tree(self, last_node, functions, level):
		if level == 3:
			return last_node
		
		get_nodes_function = functions[level]

		tree = {}
		nodes = get_nodes_function(last_node)

		for k in nodes.keys():
			v = nodes[k]

			t = self.build_tree(v, functions, level + 1)

			if t:
				tree[k] = t

		return tree

	def on_load(self):
		try:
			t = [self.get_nodes_from_scratch, self.get_nodes_from_module, self.get_nodes_from_option]
			self._table = self.build_tree(None, t, 0)
		except:
			import traceback
			print sys.exc_info(), traceback.extract_tb(sys.exc_info()[2])

	def get_members_by_name(self, members, name):
		l = []

		for member in members:
			if member.lower().startswith(name.lower()):
				l.append(member)

		return l
