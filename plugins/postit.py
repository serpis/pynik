# coding: utf-8

import sys
from commands import Command

class PostitCommand(Command): 
	hooks = ['on_join']   

	def __init__(self):
		pass
	
	def on_join(self, bot, source, channel, network, **kwargs):
		bot.tell(network, "#pynik", "O.o")
		bot.tell(network, channel, "oi")
