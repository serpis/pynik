# coding: utf-8

from commands import Command
import re
import utility
from urllib import urlencode

_get_temp_re = re.compile('^\s*(.+)\s*$')

class TempCommand(Command):
	def __init__(self):
		pass

	def trig_temp(self, bot, source, target, trigger, argument):
		"""Usage: .temp [City] | Uses data from temperatur.nu"""
		argument = argument.strip()
		if argument:
			argument = argument.strip()
			self.places[source] = argument
			self.save()
		else:
			if source in self.places:
				argument = self.places[source]
			else:
				argument = 'ryd'


		argument_text = argument
		argument = utility.asciilize(argument)
		argument = utility.escape(argument)

		# awesome hack to include avesta!
		if argument.lower() == "avesta":
			actual_argument = "fors"
		else:
			actual_argument = argument

		url = "https://www.temperatur.nu/termo/gettemp.php?" + urlencode({"stadname": actual_argument.lower(), "what": "temp"})
		response = utility.read_url(url)
		m = None

		if response:
			data = response["data"]
			m = _get_temp_re.match(data)

		if m and m.group(1) != "not found":
			return "Temperature in %s: %s." % (argument_text, m.group(1))
		else:
			return "Temperature in %s: invalid place, try using .yr instead." % (argument_text)

	def save(self):
		utility.save_data("places", self.places)

	def on_load(self):
		self.places = utility.load_data("places", {})

	def on_unload(self):
		self.places = {}
