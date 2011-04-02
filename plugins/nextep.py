# -*- coding: utf-8 -*-

from commands import Command
import re
import utility

class NextEpisodeCommand(Command):
	api_url = "http://services.tvrage.com/tools/quickinfo.php?show=%s"
	search_url = "http://tvrage.com/search.php?search=%s"
	pattern = re.compile(r"(.+?)@(.+)")
	usage = "Usage: .nextep Name of TV Show"

	def __init__(self):
		pass

	def fetch_tv_info(self, show):
		info = {}
		data = utility.read_url(self.api_url % show)["data"]
		for m in self.pattern.finditer(data):
			info[m.group(1)] = m.group(2)
		return info

	def trig_nextep(self, bot, source, target, trigger, argument):
		"""Information about the latest and next episode of a TV show."""

		# Sanitize argument
		argument = utility.escape(argument.strip())

		if not argument:
			return self.usage

		# Fetch data
		info = self.fetch_tv_info(argument)
		if "Show Name" not in info:
			return "TV show not found | Manual search: " + (self.search_url % argument)
		
		# Name of TV series
		name = info["Show Name"]

		# Premiere year
		if "Premiered" in info:
			name += " (" + info["Premiered"] + ")"
		
		# Latest episode
		if "Latest Episode" in info:
			last_ep = info["Latest Episode"].replace("^", ", ")
		else:
			last_ep = "Unknown"

		# Next episode
		if "Next Episode" in info:
			next_ep = info["Next Episode"].replace("^", ", ")
		else:
			next_ep = "Unknown"
			if "Status" in info:
				next_ep += " - " + info["Status"].replace("^", ", ")
		
		# Info URL
		if "Show URL" in info:
			url = info["Show URL"]
		else:
			url = self.search_url % argument
		
		# Compose result
		return "%s | Latest: %s | Next: %s | Read more: %s" % (name, last_ep, next_ep, url)
			
