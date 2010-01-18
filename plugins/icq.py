# coding: utf-8

import re
import utility
from commands import Command

def icq_lookup(icqid):
	url = 'http://www.icq.com/people/about_me.php?uin=' + utility.escape(icqid)
	response = utility.read_url(url)
	data = response["data"].replace("\n", "")

	m = re.search('<div class="uinf-2-2-2-1">(.*?)<\/div>.*?<div class="uinf-2-2-2-2">(.*?)<\/div>.*?<div class="uinf-2-2-2-4">(.*?)<\/div>.*?<div class="uinf-2-2-2-4">(.*?)<\/div>', data)

	if m:
		nick = m.group(1)
		info = m.group(2)
		if info:
			info = re.sub("\n|\r\n|\n\n",", ",info)
		city = m.group(3)
		country = m.group(4)
		
		if nick:
			result = nick
		if info or city or country:
			result = result + ": "
			
		if info:
			result = result + info
		if city:
			result = result + ", " + city
		if country:
			result = result + ", " + country
		return result
	else:
		return None
				
class icq(Command):
	
	def trig_icq(self, bot, source, target, trigger, argument):
		
		result = icq_lookup(argument)

		if result == None:
			return "No result returned."

		fixedline = re.sub("\s+"," ", result)
		
		return fixedline
