# coding: utf-8

# Simple adaptation of insult, by ampleyfly

from commands import Command
import string
import random
import utility

class ComplimentCommand(Command): 
	def __init__(self): 
		pass 

	def trig_compliment(self, bot, source, target, trigger, argument):
		t = argument.strip()
		if not t:
			t = source
			
		if t == "Iradieh":
			return None
		
		compliment = random.sample(self.compliments, 1)[0]
		try:
			return compliment.replace('%s', t)
			
		except:
			return "We all know %s rules, but unfortunately the compliment I tried to use does not." % t

	def trig_addcompliment(self, bot, source, target, trigger, argument): 
		if not "%s" in argument: 
			return "Trying to add an improper compliment, booo!" 
		elif argument in self.compliments: 
			return "That compliment already exists!" 
		self.compliments.append(argument) 
		self.save() 
		return "Added compliment: %s" % argument.replace('%s', source)
	 
	def save(self):
		utility.save_data("compliments", self.compliments)
	 
	def on_load(self): 
		self.compliments = utility.load_data("compliments", [])
		 
	def on_unload(self): 
		self.compliments = None

