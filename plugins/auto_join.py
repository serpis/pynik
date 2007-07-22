import sys
from plugins import Plugin

class AutoJoinPlugin(Plugin): 
	hooks = ['on_connected']   

	def __init__(self):
		pass
	
	def on_connected(self, bot, address):
		channels = ['#anime.ava', '#starkast', '#c++.se', '#ryd', '#d1b', '#python.se', '#pynik', '#teewars-dev', '#teewars']
		#channels = ['#pynik']

		for channel in channels:
			bot.join(channel)
