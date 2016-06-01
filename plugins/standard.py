# coding: latin-1

from commands import Command
import htmlentitydefs
import string
import re
import utility
import random
import datetime

class EchoCommand(Command): 
	def __init__(self):
		pass
	
	def trig_echo(self, bot, source, target, trigger, argument):
		return argument

class HelloCommand(Command): 
	def __init__(self):
		pass
	
	def trig_hello(self, bot, source, target, trigger, argument):
		return "Hello there, %s!" % source

class TimeoutDict():
	def __init__(self, timeout_secs):
		self.d = {}
		self.timeout_secs = timeout_secs

	def get(self, key):
		if key in self.d:
			(ts, data) = self.d[key]
			now = datetime.datetime.now()
			diff_secs = (now - ts).total_seconds()
			if diff_secs < self.timeout_secs:
				#self.put(key, data, now=now)
				return data
			else:
				del self.d[key]
				return None
		else:
			return None

	def put(self, key, data, now=None):
		if not now:
			now = datetime.datetime.now()
		self.d[key] = (now, data)

class PickCommand(Command): 
	def __init__(self):
		self.old_choices = TimeoutDict(60)
	
	def trig_pick(self, bot, source, target, trigger, argument):
		choices = argument.split(" or ")
		choices = map(lambda x: x.strip(), choices)
		choices = filter(lambda choice: len(choice), choices)

		c_key = "%s,%s" % (target, source)

		if not choices:
			choices = self.old_choices.get(c_key)

		#print choices

		if choices:
			responses = [(False, "Hm... Definitely not %s."), (True, "%s!"), (True, "I say... %s!"), (False, "I wouldn't pick %s..."), (True, "Perhaps %s...")]
			choice = random.choice(choices)
			positive, response = random.choice(responses)

			if positive or len(choices) == 1:
				self.old_choices.put(c_key, None)
			else:
				choices_minus_that_one = [x for x in choices]
				choices_minus_that_one.remove(choice)

				self.old_choices.put(c_key, choices_minus_that_one)
			
			return response % choice
		else:
			return None

class InsultCommand(Command): 
	def __init__(self): 
		pass 

	def trig_insult(self, bot, source, target, trigger, argument): 
		if source == "Iradieh":
			return None
		
		t = argument.strip()
		if not t:
			t = source
		
		insult = random.sample(self.insults, 1)[0]
		try:
			return insult.replace('%s', t)
			
		except:
			return "We all know %s sucks, but so does the insult I tried to use." % t

	def trig_addinsult(self, bot, source, target, trigger, argument): 
		if not "%s" in argument: 
			return "Trying to add an improper insult, booo!" 
		elif argument in self.insults: 
			return "That insult already exists!" 
		self.insults.append(argument) 
		self.save() 
		return "Added insult: %s" % argument.replace('%s', source)
	 
	def save(self): 
		utility.save_data("insults", self.insults)
	 
	def on_load(self): 
		self.insults = utility.load_data("insults", [])
		 
	def on_unload(self): 
		self.insults = None

class RawCommand(Command):
	def trig_raw(self, bot, source, target, trigger, argument):
		if utility.has_admin_privileges(source, target):
			bot.send(argument)

class TimeCommand(Command):
	def trig_time(self, bot, source, target, trigger, argument):
		import datetime
		return datetime.datetime.now().isoformat()

class WeekCommand(Command):
	def trig_week(self, bot, source, target, trigger, argument):
		import datetime
		return "Current week: %d." % (int(datetime.datetime.now().strftime("%V")))

def is_trigger(name):
	m = re.search('^trig_.+', name)
	if m:
		return True
	else:
		return False

def remove_first_five(text):
	return text[5:]

class CommandsCommand(Command):
	def trig_commands(self, bot, source, target, trigger, argument):
		triggers = []
		for command in Command.__subclasses__():
			for trigger in command.triggers:
				if trigger not in triggers:
					triggers.append(trigger)

			l = command.__dict__
			l = filter(is_trigger, l)
			l = map(remove_first_five, l)

			for trigger in l:
				if trigger not in triggers:
					triggers.append(trigger)
		
		return "Commands: %s" % ", ".join(sorted(triggers))

class HelpCommand(Command):
	def trig_help(self, bot, source, target, trigger, argument):
		"""Help command. Use it to get information about other commands."""
		trigger_found = False
		for command in Command.__subclasses__():
			fname = "trig_" + argument
			if fname in command.__dict__:
				trigger_found = True
				f = command.__dict__[fname]
				if f.__doc__:
					return "%s: %s" % (argument, f.__doc__)
		
		if trigger_found:
			return "I can offer nothing."
		else:
			return "That's not a command! Try `help <command>`"

class AAOCommand(Command):
	triggers = ['}{|', 'åäö', 'Ã¥Ã¤Ã¶']

	def on_trigger(self, bot, source, target, trigger, argument):
			if trigger == 'åäö':
				return source+": Du använder nog Latin-1"
			elif trigger == '}{|':
				return source+": Du använder nog ISO-646"
			else:
				return source+": Du använder nog UTF-8"
			
class CollectCommand(Command):
	def trig_collect(self, bot, source, target, trigger, argument):
		import gc
		obj_count = 0
		if True:
			objects = gc.get_objects()
			obj_count = len(objects)
			types = {}
			for o in objects:
				t = type(o)

				if t in types:
					types[t] += 1
				else:
					types[t] = 1

			l = []
			for key in types:
				l.append((types[key], key))

			#print sorted(l)
		gc.set_debug(gc.DEBUG_LEAK)
		return "Collected %s objects out of %s." % (gc.collect(), obj_count)
