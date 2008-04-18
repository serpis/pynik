# coding: utf-8

import re
import sys
from plugins import Plugin
import favorites
import commands
import utility
import traceback

class TeewarsNaziPlugin(Plugin): 
	hooks = ['on_privmsg']   

	def __init__(self):
		pass
	
	def on_privmsg(self, bot, source, target, message):
		if target == '#teewars' and reduce(lambda x, y: x or y in message, ['å', 'ä', 'ö', 'Å', 'Ä', 'Ö'], False):
			bot.tell(target, 'English, please.')

	def on_load(self):
		pass
		
	def on_unload(self):
		pass
