# coding: utf-8

### teetow snodde googlefight lol
### Merola fixade viktinfo lol

import re
import utility
from commands import Command

def posten_kolli_query(kolli_id):
	url = 'http://posten.se/tracktrace/TrackConsignments_do.jsp?trackntraceAction=saveSearch&consignmentId=' + utility.escape(kolli_id)
	response = utility.read_url(url)
	data = response["data"]
	
	search = re.search('(?ims)<dt>Fr&aring;n:</dt><dd>(.*?)</dd>.*?rightcol.*h2>.*<h3>(.*?)</h3>\s*?(.*?)(<br/>|<div).*?<dt>Vikt:</dt><dd>(.*?)</dd>', data)
	
	if search:
		sender = search.group(1)
		date = search.group(2)
		status = search.group(3)
		weight = search.group(5)
		
		if date and status:
			result = "%s fr\xe5n %s | %s: %s | %s" % (weight, sender, date, re.sub("<.+?>", "", status), url)
			return result
		else:
			return None
	else:
		return None

class kolli(Command):
	def __init__(self):
		pass
	
	def trig_kolli(self, bot, source, target, trigger, argument):
		result = posten_kolli_query(argument)
		
		if result == None:
			return "Hittade ingen information."
		else:
			fixedline = re.sub("\s+"," ", result)
			return fixedline
