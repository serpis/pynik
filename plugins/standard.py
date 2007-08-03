# coding: latin-1

from commands import Command
import htmlentitydefs
import string
import re
import utility

class EchoCommand(Command): 
	def __init__(self):
		pass
	
	def trig_echo(self, bot, source, target, trigger, argument):
		bot.tell(target, argument)

class HelloCommand(Command): 
	def __init__(self):
		pass
	
	def trig_hello(self, bot, source, target, trigger, argument):
		bot.tell(target, 'hello there, ' + source + '!')
class InsultCommand(Command):
	def __init__(self):
		pass

	def trig_insult(self, bot, source, target, trigger, argument):
		t = source
		if argument:
			m = re.search('(\w+)', argument)

			if m:
				t = m.group(1)

		insults = ['just not cool', 'a little nerdy', 'a sponge', 'very smelly', 'purple', 'a pig', 'a tad strange', 'not very good looking', 'awfully dull', 'a big troll', 'a potato', 'oddly shaped', 'fairly muscular', 'not at all handy', 'a bloody pervert', 'very ordinary', 'not god']
		import random;
		insult = random.sample(insults, 1)[0]
		bot.tell(target, t + ' is ' + insult + '.')
	
	def on_load(self):
		pass

	def on_unload(self):
		pass

class RawCommand(Command):
	def trig_raw(self, bot, source, target, trigger, argument):
		if source == 'serp' or source == 'teetow':
			bot.send(argument)

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
		
		bot.tell(target, 'Commands: ' + ', '.join(sorted(triggers)) + '.')

#	def can_trigger(self, source, trigger):
#		return source in ['serp!~serp@85.8.2.181.se.wasadata.net']

asciilize = string.maketrans("åäöÅÄÖ", "aaoAAO")
_get_temp_re = re.compile('^\s*(.+)\s*$')
class TempCommand(Command):
	def trig_temp(self, bot, source, target, trigger, argument):

		if len(argument) == 0:
			argument = 'ryd'

		argument_text = argument
		argument = argument.translate(asciilize)

		url = "http://www.temperatur.nu/termo/%s/temp.txt" % argument
		data = utility.read_url(url)

		m = _get_temp_re.match(data)
	
		if m:
			bot.tell(target, 'Temperature in ' + argument_text + ': ' + m.group(1))


class GoogleCommand(Command):
	def trig_google(self, bot, source, target, trigger, argument):
		import urllib2

		url = 'http://www.google.com/search?rls=en&q=' + utility.escape(argument) + '&ie=UTF-8&oe=UTF-8'

		request = urllib2.Request(url)
		request.add_header('User-Agent', 'PynikOpenAnything/1.0 +')

		opener = urllib2.build_opener()
		web_resource = opener.open(request)
		feeddata = web_resource.read()
		web_resource.close()

		m = re.search('<td><img src=\/images\/calc_img\.gif alt=""><\/td><td>&nbsp;<\/td><td nowrap><font size=\+1><b>(.*?)<\/b>', feeddata)

		if m:
			answer = m.group(1)
			answer = answer.replace(' &#215;', '×').replace('<sup>', '^')
			answer = re.sub('<.+?>', '', answer)
			bot.tell(target, answer)
		else:
			m = re.search('<div class=g><a href="(.*?)" class=l>(.*?)<\/a>(.*?)</div>', feeddata)

			if m:

				text = utility.unescape(m.group(2))
				text = re.sub('<.+?>', '', text)

				link = m.group(1)
	
				bot.tell(target, text + ' - ' + link + ' | ' + url)
			else:
				bot.tell(target, url)

class AAOCommand(Command):
	triggers = ['åäö', 'Ã¥Ã¤Ã¶']

	def on_trigger(self, bot, source, target, trigger, argument):
		if trigger == 'åäö':
			bot.tell(target, 'Du använder nog latin-1 eller liknande')
		else:
			bot.tell(target, 'Du använder nog utf-8')
			
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
			#for key in types:
			#	l.append((types[key], key))

			#print sorted(l)
		bot.tell(target, "Collected %s objects out of %s." % (gc.collect(), obj_count))
