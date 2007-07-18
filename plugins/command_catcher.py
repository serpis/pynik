import re
import sys
import signal
from plugins import Plugin
import favorites
import commands
import traceback

class TimeoutException(Exception):
	pass

def timeout(f, timeout = 1, args = (), kwargs = {}):
	def handler(signum, frame):
		raise TimeoutException
    
	old = signal.signal(signal.SIGALRM, handler)
	signal.alarm(timeout)

	result = None
	try:
		result = f(*args, **kwargs)
	except:
		signal.alarm(0)
		raise
	finally:
		signal.signal(signal.SIGALRM, old)
	signal.alarm(0)
	return result

class CommandCatcherPlugin(Plugin): 
	hooks = ['on_privmsg']   

	def __init__(self):
		pass
	
	def on_privmsg(self, bot, source, target, tupels):
		p = re.compile('^(\S)(\S+)\s?(.*?)$')

		m = p.match(tupels[5])
		
		if m and m.group(1) == '.':
			trigger = m.group(2)
			arguments = m.group(3)

			meth_name = 'trig_' + trigger
			
			pairs = []
			
			for command_class in commands.Command.__subclasses__():
				import __builtin__
				meth = None
				try:
					meth = command_class.instance.__getattribute__(meth_name)
					pairs.append([command_class.instance, meth])
				except:
					pass
					
			for command in commands.get_commands_by_trigger(trigger):
				pairs.append([command, command.on_trigger])

			for pair in pairs:
				command, method = pair

				if command.can_trigger(source, trigger):
					m = re.search('^(.+)!', source)
					if m:
						if target == source:
							target = m.group(1)
						source = m.group(1)

					try:
						timeout(method, 10, (bot, source, target, trigger, arguments))
					except TimeoutException:
						bot.tell(target, 'Command \'' + trigger + '\' took too long to execute.')
					except:
						bot.tell(target, 'Oops. Error logged.')
						bot.tell('teetow', "%s triggered an error by typing \'%s %s\': %s." % (source, trigger, arguments, sys.exc_info()))
						bot.tell('serp', "%s triggered an error by typing \'%s %s\': %s." % (source, trigger, arguments, sys.exc_info()))

						print sys.exc_info()
						print 'Error when executing command \'', trigger, '\':', traceback.extract_tb(sys.exc_info()[2])
				else:
					bot.tell(target, 'Bwaha. Noob.')

			if not len(pairs):
				if trigger in favorites.FavoriteCommands.instance.favorites.keys():
					favorites.FavoriteCommands.instance.on_fav(bot, source, target, 'fav', trigger + ' ' + arguments)

	def on_load(self):
		pass
		
	def on_unload(self):
		pass
