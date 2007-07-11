# coding: latin-1

from __main__ import *
import __main__
from commands import Command
import htmlentitydefs

class EchoCommand(Command): 
	triggers = ['echo']   

	def __init__(self):
		pass
	
	def on_trigger(self, bot, source, target, trigger, argument):
		bot.tell(target, argument)

class InsultCommand(Command):
	triggers = ['insult']

	def __init__(self):
		pass

	def on_trigger(self, bot, source, target, trigger, argument):
		t = source
		if len(argument):
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
	triggers = ['raw']

	def on_trigger(self, bot, source, target, trigger, argument):
		if source == 'serp' or source == 'teetow':
			bot.send(argument)

class CommandsCommand(Command):
	triggers = ['commands']

	def on_trigger(self, bot, source, target, trigger, argument):
		triggers = []
		for command in Command.__subclasses__():
			for trigger in __main__.plugin_instances()[command].triggers:
				if trigger not in triggers:
					triggers.append(trigger)

		bot.tell(target, 'Commands: ' + ', '.join(sorted(triggers)) + '.')

class TempCommand(Command):
	triggers = ['temp']

	def on_trigger(self, bot, source, target, trigger, argument):
		from urllib import urlopen

		if len(argument) == 0:
			argument = 'ryd'

		argument_text = argument
		argument = argument.replace('å', 'a').replace('ä', 'a').replace('ö', 'o').replace('Å', 'A').replace('Ä', 'A').replace('Ö', 'O')

		data = urlopen('http://www.temperatur.nu/termo/' + argument + '/temp.txt').read()

		p = re.compile('^\s*(.+)\s*$')
		m = p.match(data)
	
		if m:
			bot.tell(target, 'Temperature in ' + argument_text + ': ' + m.group(1))


class GoogleCommand(Command):
	triggers = ['google']

	def on_trigger(self, bot, source, target, trigger, argument):
		from urllib import urlopen
		import urllib2

		url = 'http://www.google.com/search?client=safari&rls=en&q=' + argument.replace('+', '%2B').replace(' ', '+') + '&ie=UTF-8&oe=UTF-8'

		request = urllib2.Request(url)
		request.add_header('User-Agent', 'PynikOpenAnything/1.0 +')

		opener = urllib2.build_opener()
		feeddata = opener.open(request).read()

		m = re.search('<td><img src=\/images\/calc_img\.gif alt=""><\/td><td>&nbsp;<\/td><td nowrap><font size=\+1><b>(.*?)<\/b>', feeddata)

		if m:
			answer = m.group(1)
			answer = answer.replace(' &#215;', '×').replace('<sup>', '^')
			answer = re.sub('<.+?>', '', answer)
			bot.tell(target, answer)
		else:
			m = re.search('<div class=g><a href="(.*?)" class=l>(.*?)<\/a>(.*?)</div>', feeddata)

			if m:
				def unescape(text):
					def fromhtml(s):
						try: return htmlentitydefs.entitydefs[s.group(1)]
						except KeyError: return chr(int(s.group(1)))
					return re.sub("&#?(\w+);", fromhtml, text)

				text = unescape(m.group(2))
				text = re.sub('<.+?>', '', text)
				text = unescape(text)

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
