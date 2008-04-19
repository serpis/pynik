# coding: utf-8

import sys
from plugins import Plugin

class AutoJoinPlugin(Plugin): 
	hooks = ['on_connected']   

	def __init__(self):
		pass
	
	def on_connected(self, bot):
		channels = ['#anime.ava', '#starkast', '#c++.se', '#ryd', '#python.se', '#pynik', '#teeworlds-dev', '#teeworlds', '#d2a', '#stalverk80']
		#channels = ['#botnik']

		for channel in channels:
			bot.join(channel)
