# coding: utf-8

# plugin created by Merola

import random
from commands import Command

class ScaleCommand(Command):
	def __init_(self):
		pass
	
	def trig_scale(self, bot, source, target, trigger, argument):
		# Sanitize input
		if not argument:
			argument = "failed to provide an argument" # :)
		elif len(argument) > 200:
			argument = "overflow"
		else:
			argument = argument.strip()
		
		# Prepare
		if argument.lower() == "beaufort": # Beaufort wind force scale
			num_choices = 13
			descriptions = [
				"Calm",
				"Light air",
				"Light breeze",
				"Gentle breeze",
				"Moderate breeze",
				"Fresh breeze",
				"Strong breeze",
				"Moderate gale",
				"Fresh gale",
				"Strong gale",
				"Storm",
				"Violent storm",
				"Hurricane-force"]
			print_score_fun = lambda score: \
				str(score) + " - " + descriptions[score]
			num_slots = num_choices
			argument = "Beaufort"
			
		elif argument.lower() == "richter": # Richter magnitude scale
			num_choices = 101
			num_slots = 10
			descriptions = [
				"Micro",
				"Micro",
				"Micro",
				"Minor",
				"Light",
				"Moderate",
				"Strong",
				"Major",
				"Great",
				"Great",
				"Epic"]
			print_score_fun = lambda score: \
				str(score/10.0) + " - " + descriptions[score/10]
			argument = "Richter"
			
		elif argument.lower() == "internet": # Rigged "Internet" scale
			num_choices = 101
			num_slots = 10
			print_score_fun = lambda score: \
				str(score + 9000) + "%"
			argument = "Internet"
			
		else: # Normal percentage scale
			num_choices = 101
			num_slots = 10
			print_score_fun = lambda score: \
				str(score) + "%"
			argument = '"' + argument + '"'
		
		score = random.choice(range(num_choices))
		
		# Build the answer
		pos = score * num_slots / num_choices
		scale = "[" + pos*"=" + ">" + (num_slots - 1 - pos)*"-" + "] " + \
			print_score_fun(score)
		
		return "Your score on the " + argument + " scale is " + scale
