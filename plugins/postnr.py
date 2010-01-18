# coding: utf-8

import re
import utility
import string
import os
import pickle
from commands import Command

class PostNr(Command):
	def __init__(self):
		pass
	
	def posten_postnr_query(self, Address, Postort):
		url = 'http://www.posten.se/soktjanst/postnummersok/resultat.jspv?gatunamn=' + utility.escape(Address) + '&po=' + utility.escape(Postort)
	 
		response = utility.read_url(url)
		data = response["data"]
	 
		postnrs = {}
		for line in data.split("\n"):
			search = re.search('<TD class="firstcol">([^<]*)</TD><TD>([^<]*)</TD><TD>([^<]*)', line)
			if search:
				if postnrs.has_key(search.group(3)):
					postnrs[search.group(3)] += " & " + search.group(1) + " " + search.group(2)
				else:
					postnrs[search.group(3)] = search.group(1) + " " + search.group(2)
	 
		result = ""
		for postnr in postnrs.iterkeys():
			if len(result) != 0:
				result += ", "
			result += "%s: %s" % (postnr, postnrs[postnr])
			print postnrs[postnr]
	 
		if len(result) == 0:
			return "no result :<"
		else:
			print result
			return result

	def utf82iso(self, s):
		try:
			return s.decode("utf-8").encode("iso-8859-1")
		except:
			return s

	def trig_postnr(self, bot, source, target, trigger, argument):
		if argument:
			self.places[source] = argument
			self.save()
		else:
			if source in self.places:
				argument = self.places[source]
			else:
				argument = 'ryd'

		args = string.split(argument, ", ")

		if len(args) != 2:
			return "usage: postnr <adress>, <ort>"
		else:
			return self.posten_postnr_query(self.utf82iso(args[0]), self.utf82iso(args[1]))

	def save(self): 
		f = open(os.path.join("data", "postnr_addresses.txt"), "w") 
		p = pickle.Pickler(f) 
		p.dump(self.places) 
		f.close() 

	def on_load(self): 
		self.places = {}

		try:
			f = open(os.path.join("data", "postnr_addresses.txt"), "r") 
			unpickler = pickle.Unpickler(f) 
			self.places = unpickler.load() 
			f.close() 
		except:
			pass

	def on_unload(self): 
		self.places = {}
