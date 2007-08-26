# coding: utf-8

from __future__ import with_statement
from commands import Command
import re
import utility

class NextEpisodeCommands(Command):
	def __init__(self):
		pass

	def trig_nextep(self, bot, source, target, trigger, argument):
		url = 'http://tvrage.com/search.php?search=' + argument.replace(' ', '+')

		data = utility.read_url(url)

		m = re.search('<tr bgcolor=\'#FFFFFF\'  id="brow"><td class=\'b1\'><img width=\'15\' height=\'10\' style=\'border: 1px solid black;\' src=\'http:\/\/images.tvrage.net\/flags\/.*?.gif\'> <a  href=\'(.*?)\' >(.*?)<\/a>(<\/td>|<br>)', data)


		if m:
			url = m.group(1)
			show = m.group(2)

			last_ep = None
			last_name = None
			last_date = None

			next_ep = None
			next_name = None
			next_date = None

			data = utility.read_url(url)

			m = re.search('<b>(Latest|Last) Episode: <\/b><\/td><td><a href=\'.*?\'>\d+: (\d+x\d+) \| (.*)<\/a> \((.*?)\)', data)

			if m:
				last_ep = m.group(2)
				last_name = m.group(3)
				last_date = m.group(4)
			else:
				m = re.search('<b>(Latest|Last) Episode: <\/b><\/td><td><a href=\'.*?\'>(Movie) -- (.*)<\/a> \((.*?)\)', data)

				if m:
					last_ep = m.group(2)
					last_name = m.group(3)
					last_date = m.group(4)

			m = re.search('<b>Next Episode: <\/b><\/td><td><a href=\'.*?\'>\d+: (\d+x\d+) \| (.*?)<\/a> \((.*?)\)', data)

			if m:
				next_ep = m.group(1)
				next_name = m.group(2)
				next_date = m.group(3)

			if last_ep or next_ep:
				ret_str = show + ': Last Episode: '
				if last_ep:
					ret_str += "%s - %s (%s)" % (last_ep, last_name, last_date)
				else:
					ret_str += 'none'

				ret_str += '  |  Next Episode: '
				if next_ep:
					ret_str += "%s - %s (%s)" % (next_ep, next_name, next_date)
				else:
					ret_str += 'none'

				return ret_str
			else:
				return "Show found, but I couldn't find any relevant episode data. :("
		else:
			return "Show not found."
