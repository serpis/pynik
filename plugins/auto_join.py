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
		channels = ['#anime.ava', '#starkast', '#c++.se', '#ryd', '#python.se', '#teeworlds-dev', '#teeworlds', '#stalverk80', '#botnik', '#warpdrive', '#d08', '#java.se', '#d1d', '#hardstyle.se', '#johnbauer', '#d2006', '#d09', '#lithen', '#wow.mm']
		#channels = ['#botnik']

		for channel in channels:
			bot.join(channel)
