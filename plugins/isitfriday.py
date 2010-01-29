# coding: utf-8

import re
import utility
import string
import os
import pickle
import datetime
from commands import Command

class IsItFriday(Command):
	def __init__(self):
		pass

	def trig_isitfriday(self, bot, source, target, trigger, argument):
		""" Well doh.. """
		today = datetime.date.today().strftime("%A")
		if today == 'Friday':
			return "Yes \o/"
		elif today == 'Thursday':
			return "Soon"
		else:
			return "No"

	def save(self): 
		pass

	def on_load(self): 
		pass

	def on_unload(self): 
		pass
