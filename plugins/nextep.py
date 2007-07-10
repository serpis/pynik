# coding: latin-1

from __future__ import with_statement
from commands import Command
import re

class NextEpisodeCommands(Command):
	triggers = ['nextep']

	def __init__(self):
		pass

	def on_trigger(self, bot, source, target, trigger, argument):
		import  urllib

		url = 'http://tvrage.com/search.php?search=' + argument.replace(' ', '+')

		data = urllib.urlopen(url).read()

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

			data = urllib.urlopen(url).read()

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
				retn_str = show + ': Last Episode: '
				if last_ep:
					retn_str += last_ep + ' - ' + last_name + ' (' + last_date + ')'
				else:
					retn_str += 'none'

				retn_str += '  |  Next Episode: '
				if next_ep:
					retn_str += next_ep + ' - ' + next_name + ' (' + next_date + ')'
				else:
					retn_str += 'none'

				bot.tell(target, retn_str)
			else:
				bot.tell(target, 'Show found, but no relevant episode data found. :(')
		else:
			bot.tell(target, 'Show not found.')
