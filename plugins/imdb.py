import string
import re
import utility
from commands import Command

def imdb_info(url):
	response = utility.read_url(url)
	data = response["data"]
	
	m = re.search('<title>(.*?) \((\d+\/?I?)\)<\/title>', data)
	if m:
		title = m.group(1)
		year = m.group(2)
	else:
		title = ""
		year = ""

	m = re.search('<b>([0-9\.]+)\/10<\/b>', data)
	if m:
		rating = m.group(1)
	else:
		rating = 0

	m = re.search('<h5>Plot Summary:</h5> \n(.*?)\n<a', data)
	if m:
		tagline = "\"%s\" -" % m.group(1)
	else:
		m = re.search('<h5>Plot Outline:</h5> \n(.*?) <a', data)
		if m:
			tagline = "\"%s\" -" % m.group(1)
		else:
			tagline = ""

	m = re.findall('"\/Sections\/Genres\/(.*?)\/', data)
	if m:
		genres = ", ".join(set(m))
	else:
		genres = ""

	return "%s (%s) - Rating: %s/10 - Genre: %s - %s %s" % (title, year, rating, genres, tagline, url)

def imdb_search(name):
#	url = "http://akas.imdb.com/find?s=tt&q=%s" % name.replace(" ","+")
	url = "http://www.imdb.com/find?s=tt&q=%s" % utility.escape(name)

	response = utility.read_url(url)
	data = response["data"]

#	print url
	
	m = re.search('<title>(.*?) \((\d+)\)<\/title>', data)
	if m:
		return imdb_info(url)
	
	m = re.search('<a href="(\/(title)\/.*?)"', data)
	if m:
		url = "http://www.imdb.com%s" % m.group(1)
		return imdb_info(url)

class ImdbCommand(Command):
	def trig_imdb(self, bot, source, target, trigger, argument):
		return imdb_search(argument)
		

#imdb_search("Rob Roy")
#imdb_search("Layer Cake")
#print imdb_search("The Last King of Scotland")
#print imdb_search("Die Hard")
