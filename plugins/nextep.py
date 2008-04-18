# coding: utf-8

from __future__ import with_statement
from commands import Command
import re
import utility

class Episode:
	def __init__(self, episode, name, date):
		self.episode = episode
		self.name = name
		self.date = date

	def __str__(self):
		return "%s - %s (%s)" % (self.episode, self.name, self.date)

class NextEpisodeCommands(Command):
	def __init__(self):
		pass

	def trig_nextep(self, bot, source, target, trigger, argument):
		url = 'http://tvrage.com/search.php?search=' + argument.replace(' ', '+')

		response = utility.read_url(url)
		data = response["data"]

		m = re.search('<tr bgcolor=\'#FFFFFF\'  id="brow"><td class=\'b1\'><img width=\'15\' height=\'10\' style=\'border: 1px solid black;\' src=\'http:\/\/images.tvrage.net\/flags\/.*?.gif\'> <a  href=\'(.*?)\' >(.*?)<\/a>(<\/td>|<br>)', data)

		if m:
			url = m.group(1)
			show_name = m.group(2)

			last_ep = None
			next_ep = None

			response = utility.read_url(url)
			data = response["data"]

			m = re.search('<b>(Latest|Last) Episode: <\/b><\/td><td>.*?<a href=\'.*?\'>(\d+: )?(\d+x\d+|\S+) (\||--) (.*?)<\/a> \((.*?)\)</td>', data)

			if m:
				last_ep = Episode(m.group(3), m.group(5), m.group(6))

			m = re.search('<b>Next Episode: <\/b><\/td><td>.*?<a href=\'.*?\'>(\d+: )?(\d+x\d+|\S+) (\||--) (.*?)<\/a> \((.*?)\)</td>', data)

			if m:
				next_ep = Episode(m.group(2), m.group(4), m.group(5))

			if last_ep or next_ep:
				return "%s: Last Episode: %s | Next Episode: %s" % (show_name, last_ep, next_ep)
			else:
				return "Show found, but I couldn't find any relevant episode data. :("
		else:
			return "Show not found."
