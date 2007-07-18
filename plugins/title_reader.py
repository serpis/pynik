import sys
import re
from plugins import Plugin
from commands import Command

class TitleReaderPlugin(Command): 
	hooks = ['on_privmsg']   
	last_url = {}

	def __init__(self):
		pass
	
	def on_privmsg(self, bot, source, target, tupels):
		message = tupels[5]

		m = re.search('((http:\/\/|www.)\S+)', message)

		if m:
			self.last_url[target] = m.group(1)

	def trig_title(self, bot, source, target, trigger, argument):
		if target in self.last_url.keys():
			import urllib
		
			data = urllib.urlopen(self.last_url[target]).read()

			m = re.search('<title>(.+?)<\/title>', data, re.IGNORECASE)

			if m:
				title = m.group(1)
				title = re.sub('<.+?>', '', title)

				bot.tell(target, title)
			else:
				bot.tell(target, 'I can\'t find a title for ' + self.last_url[target]) 
		else:
			bot.tell(target, 'I haven\'t seen any urls here yet.')
