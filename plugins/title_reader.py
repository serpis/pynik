import sys
import re
from plugins import Plugin
from commands import Command

class TitleReaderPlugin(Command): 
	hooks = ['on_privmsg']   
	triggers = ['title']
	black_urls = []
	last_url = ''

	def __init__(self):
		pass
	
	def get_options(self):
		return ['black_urls']
	
	def on_privmsg(self, bot, source, target, tupels):
		message = tupels[5]

		m = re.search('((http:\/\/|www.)\S+)', message)

		if m:
			self.last_url = m.group(1)

	def on_trigger(self, bot, source, target, trigger, argument):
		import urllib
		
		data = urllib.urlopen(self.last_url).read()

		m = re.search('<title>(.+?)<\/title>', data, re.IGNORECASE)

		if m:
			title = m.group(1)
			title = re.sub('<.+?>', '', title)

			bot.tell(target, title)

	def on_load(self):
		del self.black_urls[:]

		file = open('data/black_urls.txt', 'r')

		while True:
			line = file.readline()
			if not line:
				break

			m = re.match('^(.+)$', line)
			
			if m:
				self.black_urls.append(m.group(1))

	def save(self):
		file = open('data/black_urls.txt', 'w')

		for url in self.black_urls:
			file.write(url)
			file.write('\n')

		file.close()

	def on_modified_options(self):
		self.save()
