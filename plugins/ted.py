# coding: utf-8

### teetow snodde googlefight lol
### Merola fixade viktinfo lol

import re
import utility
from commands import Command

def ted_query(rawurl):
	response = utility.read_url(rawurl)
	data = response["data"]
	search = re.search('(?ims)hs:"talks/dynamic/(.+?)".+?vu=(http://[^&]+)/.+?\.flv&', data)
	
	if search:
		hqname = search.group(1)
		baseurl = search.group(2)
		
		if hqname and baseurl:
			result = "%s/%s" % (baseurl, hqname)
			return result
		else:
			return "Read the source, but couldn't capture all the groups."
	else:
		return "Read the source, but regex failed."

class ted(Command):
	def __init__(self):
		pass
	
	def trig_ted(self, bot, source, target, trigger, argument):
		result = ted_query(argument)
		
		if result == None:
			return "I couldn't harvest the URL =/"
		else:
			return result
