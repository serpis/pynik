# coding: utf-8

from commands import Command
import re
import utility

class WikipediaCommand(Command):
	def wp_get(self, language, item):
		url = "http://%s.wikipedia.org/wiki/%s" % (language, utility.escape(item.replace(" ", "_")))

		response = utility.read_url(url)

		if not response:
			return (None, None)

		data = response["data"]
		url = response["url"]

		# sometimes there is a nasty table containing the first <p>. we can't allow this to happen!
		pattern = re.compile("<table.*?>.+?<\/table>", re.MULTILINE)

		data = re.sub(pattern, "", data)

		m = re.search("<p>(.+?)<\/p>", data)
		if m:
			data = utility.unescape(m.group(1))
			data = re.sub("<.+?>", "", data)
			data = re.sub("\[\d+\]", "", data)

			index = data.rfind(".", 0, 300)

			if index == -1:
				index = 300

			if index+1 < len(data) and data[index+1] == '"':
				index += 1

			data = data[0:index+1]

			if "Wikipedia does not have an article with this exact name." in data:
				data = None
		else:
			data = None

		return (url, data)

	def trig_wp(self, bot, source, target, trigger, argument):
		languages = ["simple", "en", "sv"]
		for language in languages:
			url, data = self.wp_get(language, argument)
			if data:
				return "%s - %s" % (data, url)

		return "I couldn't find an article... :("
