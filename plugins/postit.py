# coding: utf-8

import sys
from commands import Command

class PostitCommand(Command): 
	hooks = ['on_join']   

	def __init__(self):
		pass
	
	def on_join(self, bot, source, channel):
		bot.tell("#pynik", "O.o")
		bot.tell(channel, "oi")
