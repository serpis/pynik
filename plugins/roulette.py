# -*- coding: utf-8 -*-

# Plugin created by Merola

import random
from commands import Command

class RussianRoulette(Command):
	revolver_contents = {}
	usage = "Usage: .roulette reload | .roulette play"
	
	def __init__(self):
		pass
		
	def reload_revolver(self, channel):
		self.revolver_contents[channel] = [False, False, False, False, False, False]
		self.revolver_contents[channel][random.randint(0, 5)] = True
		return "Spinning the cylinder..."
	
	def pull_trigger(self, ircbot, nickname, channel):
		contents = self.revolver_contents.get(channel, [])
		
		if not contents:
			return "Maybe it's time to reload..."
		elif contents.pop():
			kick_command = "KICK %s %s BOOM!" % (channel, nickname)
			ircbot.send(kick_command)
			return "Poor %s :(" % nickname
		else:
			return "You survive, you lucky bastard!"
	
	def trig_roulette(self, bot, source, target, trigger, argument):
		"""Russian roulette, IRC style - Will you survive, or be kicked?"""
		
		argument = argument.strip().lower()
		
		# Show usage
		if not argument:
			return "Russian roulette! " + self.usage
				
		# Play
		elif argument == 'play':
			return self.pull_trigger(bot, source, target)
		
		# Reload
		elif argument == 'reload':
			return self.reload_revolver(target)
		
		# Unknown subcommand
		else:
			return "Unknown subcommand! " + self.usage

