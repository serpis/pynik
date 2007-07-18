from __future__ import with_statement
import pickle
import sys
import re
import utility
from plugins import Plugin
from commands import Command

class URL():
	url = ''
	title = ''
	timestamp = ''
	nick = ''
	def is_match(self, searchword):
		if re.search(searchword, self.url):
			return True
		if re.search(searchword, self.title):
			return True
		if re.search(searchword, self.nick):
			return True
		return False
	

class TitleReaderPlugin(Command): 
	hooks = ['on_privmsg']   
	black_urls = []
	urls = {}

	def __init__(self):
		pass
	
	def get_options(self):
		return ['black_urls']

	def set_title(self, target):
		import urllib
		if not re.search('http', self.urls[target].url):
			self.urls[target].url = 'http://' + self.urls[target].url
		data = urllib.urlopen(self.urls[target].url).read()

		m = re.search('<title>(.+?)<\/title>', data, re.IGNORECASE)

		if m:
			self.urls[target].title = m.group(1)
			self.urls[target].title = re.sub('<.+?>', '', self.urls[target].title)
		else:
			self.urls[target].title = None
	
	def on_privmsg(self, bot, source, target, tupels):
		message = tupels[5]

		m = re.search('((http:\/\/|www.)\S+)', message)

		if m:
			if target not in self.urls.keys():			
				self.urls[target] = URL()

			self.urls[target].url = m.group(1)
			self.urls[target].nick = source
			self.urls[target].timestamp = 'test'
			self.set_title(target)
			self.save_last_url(target)

	def save_last_url(self, target):
		list = []
		try:
			file = open('data/' + target + '-urls.txt', 'r')
			list = pickle.Unpickler(file).load()
			file.close()
		except IOError:
			pass

		file = open('data/' + target + '-urls.txt', 'w')

		list.append(self.urls[target])
		p = pickle.Pickler(file)
		p.dump(list)

		file.close()

	def trig_urlsearch(self, bot, source, target, trigger, argument):
		list = []
		resultlist = []
		match = False

		searchlist = argument.split(' ')
		try:
			file = open('data/' + target + '-urls.txt', 'r')
			list = pickle.Unpickler(file).load()
			file.close()

			for object in list:
				match = True
				for word in searchlist:
					if not object.is_match(word):
						match = False
						break
				if match:
					resultlist.append(object)

			if len(resultlist) > 0:
				print(target, 'Match: ' + resultlist[0].url)
			else:
				print(target, 'No match found')

		except IOError:
			print(target, 'I have no urls for this channel')

		

	def trig_title(self, bot, source, target, trigger, argument):
		if target in self.urls.keys():
			m = self.urls[target].title

			if m:
				print(target, m)
			else:
				print(target, 'I can\'t find a title for ' + self.urls[target].url) 
		else:
			print(target, 'I haven\'t seen any urls here yet.')

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
