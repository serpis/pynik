# coding: latin-1
	  
import os
import re
import datetime
from commands import Command
from xml.dom import minidom
import utility
import urllib
import command_catcher
import time

class RssReader:
	def parse(self, data):
		xmldoc = minidom.parseString(data)

		xmlele = xmldoc.documentElement

		self.channels = []

		for channel in xmlele.getElementsByTagName('channel'):
			items = []
			self.channels.append(items)

			for item in channel.getElementsByTagName('item'):
				members = {}
				items.append(members)

				for member in item.childNodes:
					if not re.match('^#.*', member.nodeName) and member.childNodes:
						members[member.nodeName.encode('latin-1', 'ignore')] = member.childNodes[0].nodeValue.encode('latin-1', 'ignore')

	def get_articles(self):
		articles = []

		for channel in self.channels:
			for item in channel:
				title, link = item['title'], item['link']

				pubDate = None
				try:
					pubDate = datetime.datetime.strptime(item['pubDate'][0:-6], '%a, %d %b %Y %H:%M:%S')
				except:
					pubDate = datetime.datetime.strptime(item['pubDate'][0:-4], '%a, %d %b %Y %H:%M:%S')

				articles.append([pubDate, title, link])

		return articles


class RssCommand(Command):
	subscribers = {}

	def __init__(self):
		self.next_beat = None
		self.reader = RssReader()

		self.watch_list = [['serp', 'http://www.starkast.net/index.rss', None], ['serp', 'http://rss.thepiratebay.org/0', None]]

	def get_options(self):
		return ['subscribers']

	def trig_rss(self, bot, source, target, trigger, argument):
		import urllib

		url = argument

		data = urllib.urlopen(url).read()

		self.reader.parse(data)

		articles = self.reader.get_articles()
	
		if articles:
			bot.tell(target, 'Newest: ' + ' | '.join(map(lambda x: "%s - %s" % (x[1], x[2]), articles[0:3])))
		else:
			bot.tell(target, 'I couldn\'t find any articles there. :-(')

	def trig_watch(self, bot, source, target, trigger, argument):
		m = re.match('(http:\/\/\S*)', argument)

		if m:
			url = m.group(1)

			self.watch_list.append([source, url, None])
			self.save()

			bot.tell(target, 'The feed was successfully added to your watch list. You will receive news privately.')
		else:
			bot.tell(target, 'Usage: watch <rss feed>.')

	def trig_delwatch(self, bot, source, target, trigger, argument):
		m = re.match('(\S*)', argument)

		if m:
			url = m.group(1)

			to_remove = filter(lambda x: x[1] == url and x[0] == source, self.watch_list)

			if to_remove:
				for entry in to_remove:
					self.watch_list.remove(entry)
				self.save()
				bot.tell(target, 'I found the feed and removed it from your watch list.')
			elif not filter(lambda x: x[0] == source, self.watch_list):
				bot.tell(target, 'You have no feeds in your watch list!')
			else:
				urls = map(lambda x: x[1], filter(lambda x: x[0] == source, self.watch_list))
				bot.tell(target, 'These feeds are in your watch list: %s.' % (', '.join(urls)))
			
		else:
			bot.tell(target, 'Usage delwatch <rss feed>.')

	def timer_beat(self, bot, now):
		if not self.next_beat or self.next_beat < now:
			self.next_beat = now + datetime.timedelta(0, 0, 0, 0, 5)

			save_needed = False

			for t in self.watch_list:
				nick, url, newest = t
				
				try:
					data = command_catcher.timeout(urllib.urlopen, 10, [url]).read()

					self.reader.parse(data)

					articles = self.reader.get_articles()
				
					if articles:
						articles = sorted(filter(lambda x: not newest or x[0] > newest, articles))

						if articles:
							articles.reverse()
							if not newest or articles[0][0] > newest:
								t[2] = newest = articles[0][0]
								save_needed = True

							bot.tell(nick, 'New: ' + ' | '.join(map(lambda x: "%s - %s" % (x[1], x[2]), articles[0:2])))
					else:
						bot.tell(nick, 'I couldn\'t find any articles there. :-(')
				except command_catcher.TimeoutException:
					pass
				except:
					raise

			if save_needed:
				self.save()

	def save(self):
		file = open('data/rss_watch_list.txt', 'w')

		for entry in self.watch_list:
			nick, url, newest = entry[0], entry[1], entry[2]

			if not newest:
				newest = '0'
			else:
				newest = int(time.mktime(newest.timetuple()))
			
			line = "%s %s %s" % (nick, url, newest)

			file.write(line)
			file.write('\n')

		file.close()

	def on_load(self):
		self.watch_list = []

		file = open('data/rss_watch_list.txt', 'r')
		
		while True:
			line = file.readline()
			if not line:
				break

		#with open('data/favorites.txt', 'r') as file:
		#	for line in file:
			m = re.search('^(\S+)\s+(\S+)\s+(.+)$', line)

			if m:
				user = m.group(1)
				url = m.group(2)
				newest = m.group(3)

				newest = datetime.datetime.fromtimestamp(int(newest))

				self.watch_list.append([user, url, newest])

		file.close()
	
	def on_unload(self):
		self.watch_list = []
