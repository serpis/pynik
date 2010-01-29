# coding: utf-8
import re
import utility
import string
import os
import pickle
import datetime

from commands import Command

class CountDown(Command):
	def __init__(self):
		pass

	def trig_countdown(self, bot, source, target, trigger, argument):
		""" ex: .countdown 2038-01-19 03:14:07 """
		if argument:
			argument = argument.strip()
		else:
			if source in self.thens:
				argument = self.thens[source]
			else:
				argument = '2038-01-19 03:14:07'
		
		now = datetime.datetime.now()
		try:
			then = datetime.datetime.strptime(argument, "%Y-%m-%d %H:%M:%S")
		except ValueError, ve:
			return u"Wrong format, " + unicode(ve)

		if then.year < 1900:
			return u"Sorry I can't count years before 1900."
		
		self.thens[source] = argument
		self.save()
		
		diff = then - now

		def plural(x):
			return "s" if x > 1 or x < -1 else ""

		return "%s day%s, %s hour%s, %s minute%s, %s second%s until %s." % (diff.days, plural(diff.days), diff.seconds/3600, plural(diff.seconds/3600), (diff.seconds%3600)/60, plural((diff.seconds%3600)/60), (diff.seconds%3600)%60, plural((diff.seconds%3600)%60), then.strftime("%Y-%m-%d %H:%M:%S"))

	def save(self): 
		pass
		f = open(os.path.join("data", "countdowns.txt"), "w") 
		p = pickle.Pickler(f) 
		p.dump(self.thens) 
		f.close() 

	def on_load(self):
		self.thens = {}

		try:
			f = open(os.path.join("data", "countdowns.txt"), "r") 
			unpickler = pickle.Unpickler(f) 
			self.thens = unpickler.load() 
			f.close() 
		except:
			pass

	def on_unload(self):
		self.thens = {}
