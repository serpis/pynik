# coding: utf-8

from __future__ import with_statement
import pickle
import os
import re
import datetime
from commands import Command
from xml.dom import minidom
import utility
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
					if not re.match('^#.*', member.nodeName) and member.childNodes and member.nodeName and member.childNodes[0].nodeValue:
						members[member.nodeName.encode('latin-1', 'ignore')] = member.childNodes[0].nodeValue.encode('latin-1', 'ignore')

		xmldoc.unlink()

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

				# hack to please #teewars-dev
				m = re.search('^Ticket #(\d+)', title)
				if m and 'description' in item:
					title = "Ticket #%s: %s" % (m.group(1), item['description'])

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
		url = argument

		response = utility.read_url(url)

		if not response:
			return "Couldn't fetch feed."

		data = response["data"]

		self.reader.parse(data)

		articles = self.reader.get_articles()
	
		if articles:
			return 'Newest: ' + ' | '.join(map(lambda x: "%s - %s" % (x[1], x[2]), articles[0:3]))
		else:
			return 'I couldn\'t find any articles there. :-('

	def trig_watch(self, bot, source, target, trigger, argument):
		m = re.search('(http:\/\/\S*)', argument)

		if m:
			url = m.group(1)

			self.watch_list.append([source, url, datetime.datetime(datetime.MINYEAR, 1, 1)])
			self.save()

			return 'The feed was successfully added to your watch list. You will receive news privately.'
		else:
			return 'Usage: watch <rss feed>.'

	def trig_delwatch(self, bot, source, target, trigger, argument):
		m = re.match('(\S*)', argument)

		if m:
			url = m.group(1)

			to_remove = filter(lambda x: x[1] == url and x[0] == source, self.watch_list)

			if to_remove:
				for entry in to_remove:
					self.watch_list.remove(entry)
				self.save()
				return 'I found the feed and removed it from your watch list.'
			elif not filter(lambda x: x[0] == source, self.watch_list):
				return 'You have no feeds in your watch list!'
			else:
				urls = map(lambda x: x[1], filter(lambda x: x[0] == source, self.watch_list))
				return 'These feeds are in your watch list: %s.' % (', '.join(urls))
			
		else:
			return 'Usage delwatch <rss feed>.'

	def timer_beat(self, bot, now):
		if not self.next_beat or self.next_beat < now:
			self.next_beat = now + datetime.timedelta(0, 0, 0, 0, 2)

			save_needed = False

			for t in self.watch_list:
				nick, url, newest = t
				
				try:
					response = utility.timeout(utility.read_url, 10, [url])
					if not response:
						continue

					data = response["data"]

					self.reader.parse(data)

					articles = self.reader.get_articles()

					if articles:
						articles = sorted(filter(lambda x: not newest or x[0] > newest, articles))

						if articles:
							articles.reverse()
							if not newest or articles[0][0] > newest:
								t[2] = newest = articles[0][0]
								save_needed = True

							bot.tell(nick, 'New: ' + ' | '.join(map(lambda x: "%s - %s" % (x[1], x[2]), articles[0:3])))
					#else:
					#	bot.tell(nick, 'I couldn\'t find any articles there. :-(')
				except utility.TimeoutException:
					pass
				except:
					raise

			if save_needed:
				self.save()

	def save(self):
		with open('data/rss_watch_list.txt', 'w') as file:
			p = pickle.Pickler(file)

			p.dump(self.watch_list)

	def on_load(self):
		self.watch_list = []

		try:
			with open('data/rss_watch_list.txt') as file:
				unp = pickle.Unpickler(file)

				self.watch_list = unp.load()
		except:
			pass
	
	def on_unload(self):
		self.watch_list = []
