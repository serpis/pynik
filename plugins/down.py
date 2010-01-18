# coding: utf-8

### teetow snodde googlefight lol

import re
import utility
from commands import Command

class down(Command):
	def __init__(self):
		pass

	def trig_down(self, bot, source, target, trigger, argument):

		queriedUrl = argument.strip()
		if not queriedUrl:
			return "usage: .down http://example.url"

		url = 'http://downforeveryoneorjustme.com/' + utility.escape(queriedUrl)

		response = utility.read_url(url)
		data = response["data"]

		search = re.search(r'<div id\=\"container\">\s+(.+)<p>.+?<\/p>.+<\/div>', data, re.S)

		if search:
			message = search.group(1)
			message = re.sub(r'<[^>]*?>', '', message)
			return message

		else:
			return "No result. downforeveryoneorjustme.com might be down. Oh, the irony."

