# -*- coding: utf-8 -*-

import utility
from commands import Command

from json import JSONDecoder

class IMDbCommand(Command):
	usage = "Usage: .imdb <search term>"
	
	def __init__(self):
		pass

	def query(self, argument):
		decoder = JSONDecoder()
		argument = utility.escape(argument)
                api_url = u"http://www.omdbapi.com/?t=%(search_term)s&r=json&plot=short" % \
                                {"search_term": argument}
		site_search_url = u"http://akas.imdb.com/find?s=all&q=" + argument
		response = utility.read_url(api_url)

		if not response:
			return u"Couldn't connect to the API :( | Manual search: " + site_search_url

		try:
			data = decoder.decode(response['data'])
		except Exception:
			return u"Couldn't parse the API output :( | Manual search: " + site_search_url
		
		if data.get(u"Response") != u"True":
			return u"No results found! Maybe you should try searching manually: " + \
					site_search_url

		return \
				(u"%(title)s (%(year)s) - Rating: %(rating)s out of 10 - Genre: %(genre)s - " + \
				u"http://akas.imdb.com/title/%(id)s/ | More results: %(site_search_url)s") % \
				{u"title": data.get(u"Title", u"Missing title :S"),
					u"year": data.get(u"Year", u"Unknown year"),
					u"rating": data.get(u"imdbRating", u"N/A"),
					u"genre": data.get(u"Genre", u"Unknown"),
					u"id": data.get(u"imdbID", u"tt0107838"),
					u"site_search_url": site_search_url}
		
	def trig_imdb(self, bot, source, target, trigger, argument):
		"""Command that queries IMDb - The Internet Movie Database."""
		
		argument = argument.strip()
		
		# Show usage
		if not argument:
			return "IMDb - The Internet Movie Database. " + self.usage
				
		# Query API
		else:
			return self.query(argument).encode("utf-8")

