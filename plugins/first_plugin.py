# coding: utf-8

import sys
from plugins import Plugin

class FirstPlugin(Plugin): 
	hooks = ['on_privmsg']   

	def __init__(self):
		pass
	
	def on_privmsg(self, bot, source, target, message): 
		pass
