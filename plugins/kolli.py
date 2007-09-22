# coding: utf-8

### teetow snodde googlefight lol

import re
import utility
from commands import Command

def posten_kolli_query(KolliID):
	url = 'http://posten.se/tracktrace/TrackConsignments_do.jsp?trackntraceAction=saveSearch&consignmentId=' + utility.escape(KolliID)

	data = utility.read_url(url)

###	search = re.search('rightcol.*h2>(.*?)<div.*', data)
	search = re.search('(?ims)rightcol.*h2>.*<h3>(.*?)</h3>\s*?(.*?)<div.*', data)

	if search:
		date = search.group(1)
		status = search.group(2)

		if date and status:
		   result = date + ":" + re.sub("<.+?>", "", status)
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
  		   return "No result returned."

		fixedline = re.sub("\s+"," ", result)
		
		return fixedline
