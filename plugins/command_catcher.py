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

			flag = 0

			for command in commands.get_commands_by_trigger(trigger):
				try:
					flag = 1
					timeout(command.on_trigger, 10, (bot, source, target, trigger, arguments))
					#command.on_trigger(bot, source, target, trigger, arguments)
				except TimeoutException:
					bot.tell(target, 'Command \'' + trigger + '\' took too long to execute.')
				except:
					bot.tell(target, str(sys.exc_info()))
					print 'Error when executing command \'', trigger, '\':', traceback.extract_tb(sys.exc_info()[2])

			if not flag:
				if trigger in favorites.FavoriteCommands.instance.favorites.keys():
					favorites.FavoriteCommands.instance.on_fav(bot, source, target, 'fav', trigger + ' ' + arguments)

	def on_load(self):
		pass
		
	def on_unload(self):
		pass
