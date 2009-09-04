# coding: utf-8

import sys
import time
from plugins import Plugin

def get_plugins():
	return [AutoJoinPlugin()]

class AutoJoinPlugin(Plugin): 
	def __init__(self):
		pass
	
	def on_connected(self, bot):
		channels = ['#anime.ava', '#starkast', '#c++.se', '#ryd', '#python.se', '#teeworlds-dev', '#teeworlds', '#d2a', '#stalverk80', '#botnik', '#warpdrive', '#d08', '#java.se', '#d1d', '#hardstyle.se', '#johnbauer', '#d4a', '#d09', '#lithen']
		#channels = ['#botnik']

		for channel in channels:
			bot.join(channel)
