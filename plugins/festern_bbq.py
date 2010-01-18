# -*- coding: utf-8 -*-

# Plugin created by Merola

import utility
from commands import Command

class Festern_BBQ(Command):
	location = "okänt"
	
	def __init__(self):
		pass

	def on_load(self):
		self.location = utility.load_data('festern_bbq', "okänt")

	def set_location(self, value):
		self.location = value
		utility.save_data('festern_bbq', self.location)
		
	def get_location(self):
		return self.location
		
	def trig_grillern(self, bot, source, target, trigger, argument):
		# TODO Should be #festern, but botnik is not there :/
		if target == '#d1d':
			argument = argument.strip()
			
			if not argument:
				return "Det magnifika grilldonets position bokförs givetvis mycket noga. Just nu befinner det sig hos/på/i: " + self.get_location()
			
			elif argument == self.get_location():
				return "Öh, ja... Där är grilldonet."
			
			else:
				result = "OBS! Grilldonet har flyttats från " + self.get_location() + " till " + argument + "!"
				self.set_location(argument)
				return result

