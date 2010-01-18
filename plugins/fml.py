# -*- coding: utf-8 -*-

# Plugin created by Merola

import re
import string
import utility
from xml.dom import minidom
from commands import Command

def get_node_text(node):
	text = ""
	
	for child in node.childNodes:
		if child.nodeType == child.TEXT_NODE:
			text += child.data
	
	return text

def get_fml_dom(identifier, lang):
	url = "http://api.betacie.com/view/" + identifier + \
			"/nocomment?key=readonly&language=" + lang
	response = utility.read_url(url)
	data = response["data"]
	return minidom.parseString(data)

def base_fml_url(lang):
	if lang == "se":
		return "http://www.fanformittliv.com/"
	else:
		return "http://www.fmylife.com/"

def fml_entry(identifier, lang):
	dom = get_fml_dom(identifier, lang)
	result = ""
	
	if dom.getElementsByTagName("code")[0] == "0":
		if lang == "se":
			result = "Idag lyckades jag inte använda API:et. FFML"
		else:
			result =  "Today, I could not use the API. FML"
		return result + " | " + base_fml_url(lang)
	
	items = dom.getElementsByTagName("items")[0].getElementsByTagName("item")
	
	if not items:
		if lang == "se":
			result = "Idag lyckades jag inte hitta något resultat. FFML"
		else:
			result = "Today, I could not find a result. FML"
		return result + " | " + base_fml_url(lang)
	
	item = items[0]
	
	return get_node_text(item.getElementsByTagName("text")[0]) + " | " + \
			"+" + get_node_text(item.getElementsByTagName("agree")[0]) + " / " + \
			"-" + get_node_text(item.getElementsByTagName("deserved")[0]) + \
			" | " + base_fml_url(lang) + \
			get_node_text(item.getElementsByTagName("category")[0]) + "/" + \
			item.getAttribute("id")

class FMLCommand(Command):
	types = ['last', 'random', 'top', 'top_day', 'top_week', 'top_month', 'flop',
			'flop_day', 'flop_week', 'flop_month', 'love', 'money', 'kids',
			'work', 'health', 'sex', 'miscellaneous']
	
	usage = "Usage: .fml <type> | .fml <id> | .fml show_types"
	
	def __init__(self):
		pass
		
	def trig_fml(self, bot, source, target, trigger, argument):
		"""Command used to display stories from www.fmylife.com"""
		
		# Sanitize argument
		argument = argument.strip().lower()
		
		if argument:
			m = re.match("http:\/\/www\.fmylife\.com\/\w+\/(\d+)", argument)
			result = ""
			
			# Show all types, if requested
			if argument == 'show_types':
				result = "Available FML types: " + ", ".join(self.types)
			
			# If the argument is a valid type, look it up
			elif (argument in self.types) or (argument.isdigit()):
				result = fml_entry(argument, "en")
			elif m:
				result = fml_entry(m.group(1), "en")
			
			if result:
				# Return result (encoded to make IRCClient.send() happy)
				return result.encode('utf-8', 'replace')
		
		# Non-valid argument
		return self.usage

class FFMLCommand(Command):
	types = ['last', 'random', 'top', 'top_day', 'top_week', 'top_month', 'flop',
			'flop_day', 'flop_week', 'flop_month', 'karlek', 'pengar', 'barn',
			'arbete', 'halsa', 'sex', 'annat']
	
	usage = "Användning: .fml <typ> | .fml <id> | .fml visa_typer"
	
	def __init__(self):
		pass
		
	def trig_ffml(self, bot, source, target, trigger, argument):
		"""Kommando för att visa anekdoter från www.fanformittliv.com"""
		
		# Sanitize argument
		argument = argument.strip().lower()
		argument = utility.asciilize(argument)
		
		if argument:
			m = re.match("http:\/\/www\.fanformittliv\.com\/\w+\/(\d+)", argument)
			result = ""
			
			# Show all types, if requested
			if argument == 'visa_typer':
				result = "Tillgängliga typer: " + ", ".join(self.types)
			
			# If the argument is a valid type, look it up
			elif (argument in self.types) or (argument.isdigit()):
				result = fml_entry(argument, "se")
			elif m:
				result = fml_entry(m.group(1), "se")
			
			if result:
				# Return result (encoded to make IRCClient.send() happy)
				return result.encode('utf-8', 'replace')
		
		# Non-valid argument
		return self.usage
