# coding: utf-8

from __future__ import with_statement
from commands import Command
import re
import utility
import urllib

class NextEpisodeCommands(Command):
	TVRAGE_URL = "http://services.tvrage.com/tools/quickinfo.php?show=%s"
	PATTERN = re.compile(r"(.*?)@(.*)")
	def __init__(self):
		pass

	def fetch_tv_info(self,show):
		info = {}
		f = urllib.urlopen(self.TVRAGE_URL % urllib.quote(show))
		for line in f:
			m = self.PATTERN.search(line)
			if m != None:
				info[m.group(1)] = m.group(2)
		return info


	def trig_nextep(self, bot, source, target, trigger, argument):
		if len(argument): 			
			info = self.fetch_tv_info(argument)
			if "Show Name" in info:
				if "Next Episode" in info:
					next_ep = info["Next Episode"].replace("^", ", ")
				else:
					next_ep = "No Info"
					
				if "Latest Episode" in info:
					last_ep = info["Latest Episode"].replace("^", ", ")
				else:
					last_ep = "No Info"
			
				name = info["Show Name"]
			
				return "(%s): Latest: %s | Next: %s" % (name,last_ep,next_ep)
			else:
				return "Show not found."
