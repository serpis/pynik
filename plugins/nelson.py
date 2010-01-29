# coding: utf-8

import re
import utility
import string
import os
import pickle
from commands import Command

class Nelson(Command):
	def __init__(self):
		pass
	
	def trig_nelson(self, bot, source, target, trigger, argument):
		nelson = "louie"
		if argument:
			nelson = argument
		if source == "louie" or source == "LOUIE":
			nelson = source

		return "%s: http://www.youtube.com/watch?v=rX7wtNOkuHo !nocache" % nelson
