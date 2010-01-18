# coding: utf-8

### teetow snodde googlefight lol

import re
import utility
from commands import Command

class metacritic(Command):
	def __init__(self):
		pass


	def parse_result(self, response, term, fullurl):
		rslt = re.search(r'a total of <b>(?P<numresults>\d+) result.+?<p><br>View Results.+?<p>1. <strong>(?P<platform>.+?):</strong>.+?<b>(?P<title>.+?)</b>.+?\((?P<year>\d+)\).+?<SPAN.+?>(?P<score>.+?)</SPAN>.+?<br>(?P<publisher>.+?)</p>', response, re.S)

		if rslt:
			if (rslt.group('numresults') == '1'):
				return "%s (%s, %s, %s): %s" % (rslt.group('title'), rslt.group('year'), rslt.group('publisher'), rslt.group('platform'), rslt.group('score'))
			else:
				return "%s (%s, %s, %s): %s          %s (%s hits)" % (rslt.group('title'), rslt.group('year'), rslt.group('publisher'), rslt.group('platform'), rslt.group('score'), fullurl, rslt.group('numresults'))
		else:
		    return None


	def trig_mc(self, bot, source, target, trigger, argument):
		term = argument.strip()

		if not term:
			return "usage: .metacritic <game title> or <game> <platform> (slower)"

		url = 'http://apps.metacritic.com/search/process?ty=3&tfs=game_title&ts=' + utility.escape(term)
		data = utility.read_url(url)["data"]
		result = self.parse_result(data, term, url)

		if result:
			return result

		print "title search failed."
		url = 'http://apps.metacritic.com/search/process?ty=3&ts=' + utility.escape(term)
		data = utility.read_url(url)["data"]
		result = self.parse_result(data, term, url)

		if result:
			return result

		return "Found nothing. Try it yourself: " + 'http://apps.metacritic.com/search/process?ty=3&ts=' + utility.escape(term)

