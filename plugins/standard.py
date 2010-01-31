# coding: utf-8

from commands import Command
import htmlentitydefs
import string
import re
import utility
import random

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

class PickCommand(Command): 
	def __init__(self):
		pass
	
	def trig_pick(self, bot, source, target, trigger, argument):
		choices = argument.split(" or ")
		choices = map(lambda x: x.strip(), choices)
		choices = filter(lambda choice: len(choice), choices)

		#print choices

		if choices:
			responses = ["Hm... Definitely not %s.", "%s!", "I say... %s!", "I wouldn't pick %s...", "Perhaps %s..."]
			choice = random.choice(choices)
			response = random.choice(responses)
			
			return response % choice
		else:
			return None

class InsultCommand(Command): 
	def __init__(self): 
		pass 

	def trig_insult(self, bot, source, target, trigger, argument): 
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
	def trig_raw(self, bot, source, target, trigger, argument, network, **kwargs):
		if utility.has_admin_privileges(source, target):
			bot.send(network, argument)

class TimeCommand(Command):
	def trig_time(self, bot, source, target, trigger, argument):
		import datetime
		return datetime.datetime.now().strftime("%y%m%d-%H%M%S - %H:%M:%S %a %d %b w:%V")

	def trig_date(self, bot, source, target, trigger, argument):
		return self.trig_time(bot, source, target, trigger, argument)

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

_get_temp_re = re.compile('^\s*(.+)\s*$')
class TempCommand(Command):
	def __init__(self):
		pass

	def trig_temp(self, bot, source, target, trigger, argument):
		""" Usage: .temp [City] Uses data from temperature.nu, please direct all complaints to www.temperatur.nu """
		argument = argument.strip()
		if argument:
			argument = argument.strip()
			self.places[source] = argument
			self.save()
		else:
			if source in self.places:
				argument = self.places[source]
			else:
				argument = 'ryd'


		argument_text = argument
		argument = utility.asciilize(argument)
		argument = utility.escape(argument)

		# awesome hack to include avesta!
		if argument.lower() == "avesta":
			actual_argument = "fors"
		else:
			actual_argument = argument

		url = "http://www.temperatur.nu/termo/%s/temp.txt" % actual_argument
		response = utility.read_url(url)
		m = None

		if response:
			data = response["data"]
			m = _get_temp_re.match(data)

		if m and m.group(1) != "not found":
			return "Temperature in %s: %s." % (argument_text, m.group(1))
		else:
			return "Temperature in %s: invalid place, try using .yr instead." % (argument_text)

	def save(self): 
		utility.save_data("places", self.places)

	def on_load(self):
		self.places = utility.load_data("places", {})

	def on_unload(self): 
		self.places = {}

class GoogleCommand(Command):
	def trig_google(self, bot, source, target, trigger, argument):
		url = 'http://www.google.com/search?rls=en&q=' + utility.escape(argument) + '&ie=UTF-8&oe=UTF-8'

		response = utility.read_url(url)

		data = response["data"]

		#print data

		# try to extract video result
		m = re.search(r'Video results for <em>.*?<\/em>.*?<td valign=top style="padding-right:10px"><a href="(.*?)" class=l.*?>(.*?)</a><br>',data)
		if m:
			text = utility.unescape(m.group(2))
			text = re.sub('<.+?>', '', text) 
			link = m.group(1)
			return "%s - %s | %s" % (text, link, url) 

		# try to extract calculator result
		m = re.search('<td><img src="\/images\/icons\/onebox\/calculator-40\.gif" ?width=40 height=40 alt=""><td>&nbsp;<td style="vertical-align:top" >(<h2 class=r( style="font-size:\d+%")?>)?<b>(.*?)<\/b>', data)
		#m = re.search('<td><img src=\/images\/calc_img\.gif width=40 height=30 alt=""><td>&nbsp;<td style="vertical-align:top" >(<h2 class=r( style="font-size:\d+%")?>)?<b>(.*?)<\/b>', data)
		if m:
			answer = m.group(3)
			answer = answer.replace(' &#215;', '\xd7').replace('<sup>', '^')
			answer = re.sub('<.+?>', '', answer)
			return answer

		# try to extract definition
		m = re.search('<img src="\/images\/dictblue\.gif" width=40 height=30 alt=""><td valign=top.*?>(.*?)<br>', data)
		if m:
			definition = utility.unescape(m.group(1))
			definition = re.sub('<.+?>', '', definition)
			return definition

		# try to extract weather
		m = re.search('<b>Weather<\/b> for <b>(.+?)<\/b>.+?<b>(-?\d+).*C<\/b>.+?Current: <b>(.+?)<\/b>', data)

		if m:
			location = m.group(1)
			temperature = m.group(2)
			weather = m.group(3)
			return "%s: %s - %s" % (location, temperature, weather)

		# try to extract time
		m = re.search('alt=""><td valign=middle><b>(.*?)<\/b> .+?day \((.*?)\) - <b>Time</b> in (.*?)<\/table>', data)

		if m:
			time = m.group(1)
			timezone = m.group(2)
			location = m.group(3)
			location = re.sub('<.+?>', '', location)

			return "Time in %s: %s (%s)" % (location, time, timezone)
			
		
		
		# try to extract first hit
		m = re.search('<li class=g><h3 class=r><a href="(.*?)".*?>(.*?)<\/a>(.*?)</div>', data)
		if m:
			text = utility.unescape(m.group(2))
			text = re.sub('<.+?>', '', text)

			link = m.group(1)

			return "%s - %s | %s" % (text, link, url)
		else:
			return url

class WikipediaCommand(Command):
	def wp_get(self, language, item):
		url = "http://%s.wikipedia.org/wiki/%s" % (language, utility.escape(item.replace(" ", "_")))

		response = utility.read_url(url)

		if not response:
			return (None, None)

		data = response["data"]
		url = response["url"]
		
		# sometimes there is a nasty table containing the first <p>. we can't allow this to happen!
		pattern = re.compile("<table.*?>.+?<\/table>", re.MULTILINE)

		data = re.sub(pattern, "", data)

		m = re.search("<p>(.+?)<\/p>", data)
		if m:
			data = utility.unescape(m.group(1))
			data = re.sub("<.+?>", "", data)
			data = re.sub("\[\d+\]", "", data)

			index = data.rfind(".", 0, 300)

			if index == -1:
				index = 300

			if index+1 < len(data) and data[index+1] == '"':
				index += 1

			data = data[0:index+1]

			if "Wikipedia does not have an article with this exact name." in data:
				data = None
		else:
			data = None

		return (url, data)

	def trig_wp(self, bot, source, target, trigger, argument):
		languages = ["simple", "en", "sv"]
		for language in languages:
			url, data = self.wp_get(language, argument)
			if data:
				return "%s - %s" % (data, url)
	
		return "I couldn't find an article... :("

class AAOCommand(Command):
	triggers = ['}{|', '\xe5\xe4\xf6', 'åäö']

	def on_trigger(self, bot, source, target, trigger, argument):
			if trigger == '\xe5\xe4\xf6':
				return source + u": Du använder nog Latin-1 (Testa .sayaao)"
			elif trigger == '}{|':
				return source + u": Du använder nog ISO-646 (Testa .sayaao)"
			else:
				return source + u": Du använder nog UTF-8 (Testa .sayaao)"

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
		gc.set_debug(gc.DEBUG_LEAK | gc.DEBUG_STATS)
		return "Collected %s objects out of %s. Garbarge are %s objects." % (gc.collect(), obj_count, len(gc.garbage))

	def trig_garbage(self, bot, source, target, trigger, argument):
		import gc

		gc.set_debug(0)

		garbage_cnt = len(gc.garbage[:])
		del(gc.garbage[:])
		collect_cnt = gc.collect(2)
		garbage_left = len(gc.garbage[:])

		return "Collected %s objects. Brought out %s units of garbage, %s units left." % (collect_cnt, garbage_cnt, garbage_left)
